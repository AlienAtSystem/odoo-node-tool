# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError,ValidationError
import json

TREASURE_RESULT_REFERENCE = [
    ('treasure.coin.type', 'Currency'),
    ('treasure.artifact', 'Object'),
]

class TreasureWizard(models.TransientModel):
    _name = 'treasure.table.wizard'

    treasure_table_id = fields.Many2one('treasure.table', 'Treasure Table',
                                         domain="[('id','in',allowed_table_ids)]")

    num_pulls = fields.Integer('Number of Rolls', store=True, readonly=False, compute='_compute_num_pulls')

    output_json = fields.Text("Encounter (JSON)")
    output_pretty = fields.Html("Generated Treasure", compute='_compute_pretty_output')

    # Applicability Sub-Fields
    res_model = fields.Char('Resource Model')
    res_id = fields.Many2oneReference('Resource ID', model_field="res_model")
    allow_apply = fields.Boolean('Allow Apply', default=False)

    # Pre-Selection Sub-Fields
    selected_table_ids = fields.Many2many('treasure.table', string='Possible Treasure Tables')
    use_selected_table = fields.Boolean('Only Show Relevant Tables')
    allow_selection = fields.Boolean('Allow Selection', compute='_compute_allow_selection')
    allowed_table_domain = fields.Binary(compute='_compute_allowed_tables')

    @api.constrains('num_pulls')
    def _check_pulls_positive(self):
        if self.num_pulls <= 0:
            raise ValidationError("Roll Number must be positive.")

    @api.model
    def _get_pretty_output_line(self, treasure_line):
        res_model, res_id = treasure_line.get('res_reference').split(',')
        treasure = self.env[res_model].browse(int(res_id))
        return f"{treasure_line.get('amount',0)}x {treasure.name}"

    @api.depends('output_json')
    def _compute_pretty_output(self):
        for rec in self:
            treasure_lines = json.loads(rec.output_json or "[]")
            rec.output_pretty = "<p>"+"</p><p>".join(self._get_pretty_output_line(line) for line in treasure_lines)+"</p>"

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

    @api.depends('treasure_table_id')
    def _compute_num_pulls(self):
        for rec in self:
            rec.num_pulls = rec.treasure_table_id.num_pulls

    def action_apply(self):
        self.ensure_one()
        target_model = self.env[self.res_model].browse(self.res_id).exists()
        if hasattr(target_model,'_action_apply_treasure'):
            target_model._action_apply_treasure(json.loads(self.output_json or "[]"))

    def action_generate_treasure(self):
        self.ensure_one()
        treasure_data = self._generate_treasure()
        treasure_data = self._merge_treasure_lines(treasure_data)
        self.output_json = json.dumps(treasure_data)
        action = self.env["ir.actions.actions"]._for_xml_id("treasure_tool.act_treasure_generation")
        action['res_id'] = self.id
        return action

    def _generate_treasure(self):
        self.ensure_one()
        if not self.treasure_table_id.table_line_ids:
            raise UserError("The Treasure Table has no entries.")
        self._check_pulls_positive()
        return self.treasure_table_id._generate_treasure(num_pulls_override=self.num_pulls)


    @api.model
    def _get_indentifiying_line_keys(self):
        return ['res_reference']

    @api.model
    def _merge_treasure_lines(self, treasure_lines):
        # For inheritability (like modifying treasures later), we use a separate function to merge functionally identical
        # lines in our generated encounter
        seen_keys = {}
        for line in treasure_lines:
            key = tuple(line.get(entry) for entry in self._get_indentifiying_line_keys())
            if key in seen_keys:
                seen_keys[key]['amount'] += line['amount']
            else:
                seen_keys[key] = line
        # We also clean out all 0-entries now
        return list(value for value in seen_keys.values() if value['amount']>0)