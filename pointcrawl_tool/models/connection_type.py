# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ConectionType(models.Model):
    _name = 'point.connection.type'
    _description = 'Connection Type'
    _order = 'name,id'

    name = fields.Char('Name', required=True)
    description_up = fields.Char('Upwards Description')
    description_down = fields.Char('Downwards Description')