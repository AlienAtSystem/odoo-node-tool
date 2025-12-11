# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError

class BestiaryEntry(models.Model):
    _name = 'bestiary.entry'

    _order = 'name,id'

    name = fields.Char('Name',required=True)

    description_rules = fields.Html('Statblock')
    description_lore = fields.Html('Lore')

    challenge_rating = fields.Float('Challenge Rating', default=1, required=True)

    _sql_constraints = [
        ('check_challenge_rating_positive', 'CHECK (challenge_rating > 0)',
         'Challenge Rating must be positive.'),
    ]