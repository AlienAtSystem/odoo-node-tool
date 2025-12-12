# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError

class AdversaryRosterLine(models.Model):
    _name = 'location.encounter.line'

    location_id = fields.Many2one('point.location', 'Location')

    entry_id = fields.Many2one('bestiary.entry', 'Monster')
    amount = fields.Integer('Amount')

    _sql_constraints = [
        ('check_amount_nonnegative', 'CHECK (amount >= 0)',
         "Amount can't be negative."),
    ]