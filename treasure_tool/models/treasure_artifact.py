# -*- coding: utf-8 -*-

from odoo import api, fields, models
from random import randint

class Artifact(models.Model):
    _name = 'treasure.artifact'
    _description = 'Named Treasure'
    _order = 'name,id'

    name = fields.Char(string='Name')
    value = fields.Float(string='Value')
    description_rules = fields.Html('Statblock')
    description_lore = fields.Html('Lore')
    tag_ids = fields.Many2many('treasure.artifact.tag', string='Tags')

    @property
    def average_value(self):
        return self.value

    def _generate_treasure(self, num_pulls_override=None):
        self.ensure_one()
        if num_pulls_override is not None:
            num_pulls = int(num_pulls_override)
        else:
            num_pulls = 1
        return [{'res_reference': f'treasure.artifact,{self.id}', 'amount': num_pulls}]


class ArtifactTag(models.Model):
    _name = 'treasure.artifact.tag'
    _description = 'Treasure Tag'
    _order = 'name,id'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Name')
    color = fields.Integer("Color Index", default=_get_default_color)
