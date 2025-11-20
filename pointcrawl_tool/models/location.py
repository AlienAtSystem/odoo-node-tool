# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import Command

class Location(models.Model):
    _name = 'point.location'
    _description = 'Location'
    _order = 'name,id'

    name = fields.Char('Name', required=True)
    description = fields.Html('Description')

    area_id = fields.Many2one('point.area','Area')

    connection_down_ids = fields.One2many('point.connection', 'location_up_id')
    connection_up_ids = fields.One2many('point.connection', 'location_down_id')
    connection_ids = fields.One2many('point.connection.directed', compute='_compute_connection_ids', inverse="_set_connection_ids", readonly=False)

    @api.depends('connection_down_ids','connection_up_ids')
    def _compute_connection_ids(self):
        for rec in self:
            connection_ids = rec.connection_down_ids | rec.connection_up_ids
            new_conns = self.env['point.connection.directed'].create([{'connection_id': connection.id, 'location_id': rec.id} for connection in connection_ids])
            rec.connection_ids = new_conns

    def _set_connection_ids(self):
        for rec in self:
            connections_to_add = rec.connection_ids.filtered(lambda conn: not conn.connection_id)
            for connection in connections_to_add:
                new_connection_vals = {
                    'connection_type_id': connection.connection_type_id.id,
                    'location_up_id': connection.location_id.id,
                    'location_down_id': connection.other_location_id.id,
                }
                connection.connection_id = self.env['point.connection'].create(new_connection_vals)
