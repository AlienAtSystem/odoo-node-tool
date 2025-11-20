# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Connection(models.Model):
    _name = 'point.connection'
    _description = 'Connection'
    _order = 'id'

    connection_type_id = fields.Many2one('point.connection.type', 'Type')

    location_up_id = fields.Many2one('point.location', 'Upwards Location')
    location_down_id = fields.Many2one('point.location', 'Downwards Location')

    description_up = fields.Char(related='connection_type_id.description_up')
    description_down = fields.Char(related='connection_type_id.description_down')

    def action_swap_locations(self):
        for rec in self:
            rec.location_up_id,rec.location_down_id = rec.location_down_id,rec.location_up_id

class DirectedConnection(models.TransientModel):
    _name = 'point.connection.directed'

    connection_id = fields.Many2one('point.connection', 'Parent')
    location_id = fields.Many2one('point.location', 'Source')

    connection_type_id = fields.Many2one(related='connection_id.connection_type_id', readonly=False)
    other_location_id = fields.Many2one('point.location', 'Reaching', compute="_compute_other_location", inverse="_set_other_location")
    path_description = fields.Char('Via', compute="_compute_other_location")

    @api.depends('location_id', 'connection_id', 'connection_id.location_up_id', 'connection_id.location_down_id')
    def _compute_other_location(self):
        for rec in self:
            if rec.location_id == rec.connection_id.location_up_id:
                rec.other_location_id = rec.connection_id.location_down_id
                rec.path_description = rec.connection_id.description_down
            elif rec.location_id == rec.connection_id.location_down_id:
                rec.other_location_id = rec.connection_id.location_up_id
                rec.path_description = rec.connection_id.description_up
            else:
                rec.other_location_id = False
                rec.path_description = False

    def _set_other_location(self):
        for rec in self:
            if rec.location_id == rec.connection_id.location_up_id:
                rec.connection_id.location_down_id = rec.other_location_id
            elif rec.location_id == rec.connection_id.location_down_id:
                rec.connection_id.location_up_id = rec.other_location_id

    def action_swap_locations(self):
        self.connection_id.action_swap_locations()

    def action_unlink(self):
        self.connection_id.unlink()
        self.unlink()
