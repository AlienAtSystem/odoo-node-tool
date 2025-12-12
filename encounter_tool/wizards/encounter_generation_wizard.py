# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError,ValidationError
import json
import random


class EncounterWizard(models.TransientModel):
    _name = 'bestiary.encounter.wizard'

    encounter_table_id = fields.Many2one('bestiary.encounter.table', 'Encounter Table', domain="[('id','in',allowed_table_ids)]")

    difficulty_multiplier = fields.Float("Multiplier", default=1)
    difficulty_choice = fields.Selection([
        ('0.5','Very Easy'),
        ('0.75', 'Easy'),
        ('1.0', 'Average'),
        ('1.5', 'Hard'),
        ('2.0', 'Very Hard')
    ],"Difficulty", compute='_compute_difficulty_choice', inverse='_set_difficulty_choice')

    output_json = fields.Text("Encounter (JSON)")
    output_pretty = fields.Html("Generated Encounter", compute='_compute_pretty_output')

    # Applicability Sub-Fields
    res_model = fields.Char('Resource Model')
    res_id = fields.Many2oneReference('Resource ID', model_field="res_model")
    allow_apply = fields.Boolean('Allow Apply', default=False)

    # Pre-Selection Sub-Fields
    selected_table_ids = fields.Many2many('bestiary.encounter.table', string='Possible Encounters')
    use_selected_table = fields.Boolean('Only Show Relevant Tables')
    allow_selection = fields.Boolean('Allow Selection', compute='_compute_allow_selection')
    allowed_table_domain = fields.Binary(compute='_compute_allowed_tables')

    @api.constrains('difficulty_multiplier')
    def _check_multiplier_positive(self):
        if self.difficulty_multiplier <=0:
            raise ValidationError("Difficulty Multiplier must be positive.")

    @api.depends('difficulty_multiplier')
    def _compute_difficulty_choice(self):
        for rec in self:
            rec.difficulty_choice = False

    def _set_difficulty_choice(self):
        for rec in self:
            if rec.difficulty_choice:
                rec.difficulty_multiplier = float(rec.difficulty_choice)

    @api.model
    def _get_pretty_output_line(self, encounter_line):
        monster = self.env['bestiary.entry'].browse(encounter_line.get('entry_id'))
        return f"{encounter_line.get('amount',0)}x {monster.name}"

    @api.depends('output_json')
    def _compute_pretty_output(self):
        for rec in self:
            encounter_lines = json.loads(rec.output_json or "[]")
            rec.output_pretty = "<p>"+"</p><p>".join(self._get_pretty_output_line(line) for line in encounter_lines)+"</p>"

    @api.depends('selected_table_ids')
    def _compute_allow_selection(self):
        for rec in self:
            rec.allow_selection = bool(rec.selected_table_ids)

    @api.depends('use_selected_table')
    def _compute_allowed_tables(self):
        for rec in self:
            if rec.use_selected_table:
                rec.allowed_table_domain = [('id','in', rec.selected_table_ids.ids)]
            else:
                rec.allowed_table_domain = []

    @api.model
    def _get_lanchester_parameters(self):
        cr_param = self.env['ir.config_parameter'].sudo().get_param('encounter_tool.lanchester_exponent_cr')
        n_param = self.env['ir.config_parameter'].sudo().get_param('encounter_tool.lanchester_exponent_n')
        try:
            cr_param = float(cr_param) if cr_param else False
            n_param = float(n_param) if n_param else False
        except ValueError:
            return False, False
        return cr_param, n_param

    def action_apply(self):
        self.ensure_one()
        target_model = self.env[self.res_model].browse(self.res_id).exists()
        if hasattr(target_model,'_action_apply_bestiary_encounter'):
            target_model._action_apply_bestiary_encounter(json.loads(self.output_json or "[]"))

    def action_generate_encounter(self):
        self.ensure_one()
        encounter_data = self._generate_enounter()
        encounter_data = self._merge_encounter_lines(encounter_data)
        self.output_json = json.dumps(encounter_data)
        action = self.env["ir.actions.actions"]._for_xml_id("encounter_tool.act_encounter_generation")
        action['res_id'] = self.id
        return action

    def _generate_enounter(self):
        self.ensure_one()
        cr_param, n_param = self._get_lanchester_parameters()
        if cr_param is False:
            raise UserError("The Lanchester Parameters are not set correctly.")
        if not self.encounter_table_id.table_line_ids:
            raise UserError("The Encounter Table has no entries.")
        self._check_multiplier_positive()

        # Generation works as follows:
        #   1. Randomly choose 3 lines from the table based on the tickets (might be the same)
        #   2. Determine a goal difficulty between max and min for the table, times difficulty_multiplier
        #   3. Randomly add one to the amount of the 3 lines until the difficulty is above our goal or would exceed the max

        # Part 1 - Pre-Choose lines
        chosen_lines = random.choices(self.encounter_table_id.table_line_ids,
                                      weights=self.encounter_table_id.table_line_ids.mapped('ticket_amount'),
                                      k=3)
        amounts = [0] * len(chosen_lines)
        alphas = [line.entry_challenge_rating ** cr_param for line in chosen_lines]
        tickets = [line.ticket_amount for line in chosen_lines]

        # Part 2 - goal difficulty
        min_difficulty = self.encounter_table_id.number_appearing_min ** n_param * self.encounter_table_id.average_cr ** cr_param * self.difficulty_multiplier
        max_difficulty = self.encounter_table_id.number_appearing_max ** n_param * self.encounter_table_id.average_cr ** cr_param * self.difficulty_multiplier
        goal_difficulty = random.uniform(min_difficulty,max_difficulty)

        # Part 3 - increase amounts
        def get_lanchester_rating(n_list,alpha_list):
            weighted_part = sum(entry[0]*entry[1] for entry in zip(n_list,alpha_list))
            amount_part = sum(n_list) ** (n_param - 1)
            return weighted_part * amount_part

        index = range(len(chosen_lines))
        curr_difficulty = 0
        while curr_difficulty < goal_difficulty:
            rand_index = random.choices(index,weights=tickets,k=1)[0]
            amounts[rand_index] += 1
            curr_difficulty = get_lanchester_rating(amounts, alphas)
            if curr_difficulty > max_difficulty:
                amounts[rand_index] -=1
                break

        # Now convert into data
        encounter_lines = [{
            'entry_id': entry[0].entry_id.id,
            'amount': entry[1],
        } for entry in zip(chosen_lines, amounts)]

        return encounter_lines

    @api.model
    def _get_indentifiying_line_keys(self):
        return ['entry_id']

    @api.model
    def _merge_encounter_lines(self, encounter_lines):
        # For inheritability (like modifying monsters later), we use a separate function to merge functionally identical
        # lines in our generated encounter
        seen_keys = {}
        for line in encounter_lines:
            key = tuple(line.get(entry) for entry in self._get_indentifiying_line_keys())
            if key in seen_keys:
                seen_keys[key]['amount'] += line['amount']
            else:
                seen_keys[key] = line
        # We also clean out all 0-entries now
        return list(value for value in seen_keys.values() if value['amount']>0)
