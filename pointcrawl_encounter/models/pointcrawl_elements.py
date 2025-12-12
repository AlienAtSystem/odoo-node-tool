# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import Command

class Location(models.Model):
    _inherit = ['point.location', 'bestiary.encounter.mixin']
    _name = 'point.location'

    roster = fields.One2many('location.encounter.line', 'location_id', string='Adversary Roster')

    def _get_allow_encounter_application(self):
        return True

    def _action_apply_bestiary_encounter(self, encounter_vals):
        self.ensure_one()
        new_roster_lines = self.env['location.encounter.line'].create(encounter_vals)
        self.roster |= new_roster_lines

    def action_encounter_generator(self):
        action = super().action_encounter_generator()
        tables = self.encounter_table_id
        tables |= self.area_id.encounter_table_id
        tables |= self.connection_ids.other_location_id.encounter_table_id
        tables |= self.connection_ids.other_location_id.area_id.encounter_table_id
        tables |= self.connection_ids.connection_id.area_id.encounter_table_id
        if tables:
            action['context'].update({
                'default_selected_table_ids': tables.ids,
                'default_use_selected_table': True,
            })
        return action

class Area(models.Model):
    _inherit = ['point.area', 'bestiary.encounter.mixin']
    _name = 'point.area'