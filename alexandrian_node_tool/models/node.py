# -*- coding: utf-8 -*-

from odoo import api, fields, models
from random import randint

class Node(models.Model):
    _name = 'node.node'
    _description = 'Node'
    _order = 'sequence'

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name')
    connections_in_ids = fields.One2many('node.connection','target_id', string='Incoming Clues')
    connections_in_count = fields.Integer('Clues to', compute='_compute_in_count', store=True)
    connections_out_ids = fields.One2many('node.connection', 'location_id', string='Present Clues')
    connections_out_count = fields.Integer('Clues from', compute='_compute_out_count', store=True)
    node_type = fields.Selection([('location', 'Location'),('concept', 'Conceptual')])
    tag_ids = fields.Many2many('node.tag', string='Tags')
    description = fields.Html('Description')

    @api.depends('connections_in_ids')
    def _compute_in_count(self):
        for rec in self:
            rec.connections_in_count = len(rec.connections_in_ids)

    @api.depends('connections_out_ids')
    def _compute_out_count(self):
        for rec in self:
            rec.connections_out_count = len(rec.connections_out_ids)


class Tag(models.Model):
    _name = "node.tag"
    _description = "Node Tag"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Tag Name', required=True, translate=True)
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
