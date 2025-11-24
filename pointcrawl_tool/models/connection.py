# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Connection(models.Model):
    _name = 'point.connection'
    _description = 'Connection'
    _order = 'id'

    connection_type_id = fields.Many2one('point.connection.type', 'Type')

    location_up_id = fields.Many2one('point.location', 'Upwards Location')
    location_down_id = fields.Many2one('point.location', 'Downwards Location')

    area_id = fields.Many2one('point.area', 'Area', compute='_compute_area_id', readonly=False, store=True)
    display_color = fields.Char('Display Color', compute='_compute_display_color')

    description_up = fields.Char(related='connection_type_id.description_up')
    description_down = fields.Char(related='connection_type_id.description_down')

    def action_swap_locations(self):
        for rec in self:
            rec.location_up_id,rec.location_down_id = rec.location_down_id,rec.location_up_id

    @api.depends('location_up_id', 'location_up_id.area_id', 'location_down_id', 'location_down_id.area_id')
    def _compute_area_id(self):
        for rec in self:
            new_area_ids = rec.location_up_id.area_id | rec.location_down_id.area_id
            if rec.area_id not in new_area_ids:
                rec.area_id = new_area_ids[:1]

    @api.depends('area_id', 'connection_type_id')
    def _compute_display_color(self):
        for rec in self:
            if rec.connection_type_id.color:
                rec.display_color = rec.connection_type_id.color
            elif rec.area_id:
                rec.display_color = rec.area_id.display_color
            else:
                rec.display_color = '#000000'

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
