# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from numpy import random

class CoinHoard(models.Model):
    _name = 'treasure.coin.hoard'
    _description = 'Coin Hoard'
    _order = 'average_value, id'

    coin_type_id = fields.Many2one('treasure.coin.type',
                                   "Coin Type",
                                   default=lambda self: self.env.ref('treasure_tool.coin_type_silver', raise_if_not_found=False),
                                   required=True)

    generation_method = fields.Selection([
        ('linear', 'Linear'),
        ('poisson', 'Poisson'),
        ('geometric', 'Geometric'),
    ], string="Distribution Curve", required=True, default='linear')

    param_1 = fields.Float(string='Parameter 1', compute='_compute_parameters', store=True, readonly=False)
    param_1_name = fields.Char(string='Parameter 1 Name', compute='_compute_parameter_names')
    param_2 = fields.Float(string='Parameter 2', compute='_compute_parameters', store=True, readonly=False)
    param_2_name = fields.Char(string='Parameter 2 Name', compute='_compute_parameter_names')
    param_2_display = fields.Boolean(string='Parameter 2 Display', compute='_compute_parameter_names')

    average_value = fields.Float(string='Average Value', compute='_compute_average_value', store=True)
    average_amount = fields.Float(string='Average Amount', compute='_compute_average_value', store=True)

    @api.depends('generation_method')
    def _compute_parameters(self):
        for rec in self:
            rec.param_1 = rec.param_2 = False

    @api.depends('generation_method')
    def _compute_parameter_names(self):
        for rec in self:
            if rec.generation_method == 'linear':
                rec.param_1_name = "Minimum"
                rec.param_2_name = "Maximum"
                rec.param_2_display = True
            elif rec.generation_method in ('geometric', 'poisson'):
                rec.param_1_name = "Mean"
                rec.param_2_name = "N/A"
                rec.param_2_display = False
            else:
                rec.param_1_name = "N/A"
                rec.param_2_name = "N/A"
                rec.param_2_display = False


    @api.depends('generation_method', 'coin_type_id', 'coin_type_id.value_factor', 'param_1', 'param_2')
    def _compute_average_value(self):
        for rec in self:
            if rec.generation_method == 'linear':
                mean = (round(rec.param_1) + round(rec.param_2))/2
            elif rec.generation_method in ('geometric', 'poisson'):
                mean = rec.param_1
            else:
                mean = 0.0
            rec.average_amount = mean
            rec.average_value = mean * rec.coin_type_id.value_factor

    @api.depends('coin_type_id', 'average_value', 'generation_method')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.coin_type_id.name} - {rec.average_amount} ({rec.generation_method})"

    @api.constrains('generation_method', 'param_1', 'param_2')
    def _validate_parameters(self):
        for rec in self:
            if rec.param_1 < 0:
                raise ValidationError(_('The distribution parameters cannot be negative.'))
            if rec.generation_method == 'linear':
                if rec.param_1 > rec.param_2:
                    raise ValidationError(_("The minimun can't be larger than the maximum"))
                if rec.param_2 < 0:
                    raise ValidationError(_('The distribution parameters cannot be negative.'))

    def _generate_treasure(self, num_pulls_override=None):
        self.ensure_one()
        if num_pulls_override is not None:
            num_pulls = int(num_pulls_override)
        else:
            num_pulls = 1
        rand_gen = random.default_rng()
        if self.generation_method == 'linear':
            amount = rand_gen.integers(low=round(self.param_1), high=round(self.param_2), endpoint=True)
        elif self.generation_method == 'geometric':
            amount = rand_gen.geometric(1.0/self.param_1)
        elif self.generation_method == 'poisson':
            amount = rand_gen.poisson(self.param_1)
        else:
            amount = 1
        amount *= num_pulls
        return [{'res_reference': f'treasure.coin.type,{self.coin_type_id.id}', 'amount': amount}]

class CoinType(models.Model):
    _name = 'treasure.coin.type'
    _description = 'Coin Type'
    _order = 'value_factor, name, id'

    name = fields.Char(string='Name')
    value_factor = fields.Float(string='Value Factor', required=True, default=1)