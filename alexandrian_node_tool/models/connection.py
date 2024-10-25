# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Connection(models.Model):
    _name = 'node.connection'
    _description = 'Connection'
    _order = 'id'

    name = fields.Char('Name')
    location_id = fields.Many2one('node.node', 'Location')
    target_id = fields.Many2one('node.node', 'Target')
    description = fields.Html('Description')