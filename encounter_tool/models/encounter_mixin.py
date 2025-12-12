# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError,ValidationError

class EncounterMixin(models.AbstractModel):
    _name = "bestiary.encounter.mixin"
    _description = 'Encounter Generation Mixin'

    encounter_table_id = fields.Many2one('bestiary.encounter.table', 'Encounter Table')

    def action_encounter_generator(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("encounter_tool.act_encounter_generation")
        action['context'] = {
            'default_encounter_table_id': self.encounter_table_id.id,
            'default_res_model': self._name,
            'default_res_id': self.id,
            'default_allow_apply': self._get_allow_encounter_application()
        }
        return action

    def _get_allow_encounter_application(self):
        return False

    def _action_apply_bestiary_encounter(self, encounter_vals):
        return # To be implemented in the inherited functions

