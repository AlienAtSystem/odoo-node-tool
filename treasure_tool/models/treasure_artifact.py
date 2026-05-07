# -*- coding: utf-8 -*-

from odoo import api, fields, models
from random import randint

class Artifact(models.Model):
    _name = 'treasure.artifact'
    _description = 'Named Treasure'
    _order = 'name,id'

    name = fields.Char(string='Name')
    value = fields.Float(string='Value')
    description = fields.Html(string='Description')
    tag_ids = fields.Many2many('treasure.artifact.tag', string='Tags')

    @property
    def average_value(self):
        return self.value


class ArtifactTag(models.Model):
    _name = 'treasure.artifact.tag'
    _description = 'Treasure Tag'
    _order = 'name,id'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Name')
    color = fields.Integer("Color Index", default=_get_default_color)
