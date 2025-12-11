# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError

class Area(models.Model):
    _name = 'point.area'
    _description = 'Area'
    _order = 'name,id'

    name = fields.Char('Name',required=True)
    description = fields.Html('Description')

    parent_id = fields.Many2one('point.area', 'Area')
    child_ids = fields.One2many('point.area', 'parent_id', 'Sub-Areas')

    location_ids = fields.One2many('point.location', 'area_id', 'Locations')

    color = fields.Char('Color')
    display_color = fields.Char('Display Color', compute='_compute_display_color', recursive=True)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create a recursive hierarchy of areas.'))

    @api.depends('color', 'parent_id', 'parent_id.display_color')
    def _compute_display_color(self):
        for rec in self:
            if rec.color:
                rec.display_color = rec.color
            elif rec.parent_id:
                rec.display_color = rec.parent_id.display_color
            else:
                rec.display_color = "#000000"