# -*- coding: utf-8 -*-
from decorator import n_args

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError

class BestiaryEncounterTable(models.Model):
    _name = 'bestiary.encounter.table'

    _order = 'name,id'

    name = fields.Char('Name', required=True)
    table_line_ids = fields.One2many('bestiary.encounter.table.line','table_id','Possible Creatures')

    number_appearing_min = fields.Float('Minimum Number Appearing')
    number_appearing_max = fields.Float('Maximum Number Appearing')

    average_cr = fields.Float('Average Challenge', compute='_compute_challenge_rating')

    _sql_constraints = [
        ('check_build_amount', 'CHECK (number_appearing_min <= number_appearing_max)', 'Minimum Amount may not be larger than Maximum Amount.'),
    ]


    @api.depends('number_appearing_min','number_appearing_max','table_line_ids','table_line_ids.ticket_amount','table_line_ids.entry_id')
    def _compute_challenge_rating(self):
        for rec in self:
            if not rec.table_line_ids:
                rec.average_cr = 0
                continue
            average_cr = sum(line.entry_challenge_rating * line.ticket_amount for line in rec.table_line_ids) / sum(line.ticket_amount for line in rec.table_line_ids)
            rec.average_cr = average_cr
    
    def action_encounter_generator(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("encounter_tool.act_encounter_generation")
        action['context'] = {
            'default_encounter_table_id': self.id,
        }
        return action


class BestiaryEncounterTableLine(models.Model):
    _name = 'bestiary.encounter.table.line'

    table_id = fields.Many2one('bestiary.encounter.table', 'Corresponding Table', ondelete="cascade")

    entry_id = fields.Many2one('bestiary.entry', 'Creature', required=True)
    entry_challenge_rating = fields.Float(related='entry_id.challenge_rating')
    ticket_amount = fields.Integer('Tickets', default=1, help='Number of times this entry is entered into the lottery to determine what appears.', required=True)

    _sql_constraints = [
        ('check_ticket_amount_positive', 'CHECK (ticket_amount > 0)',
         'Tickets must be positive.'),
    ]