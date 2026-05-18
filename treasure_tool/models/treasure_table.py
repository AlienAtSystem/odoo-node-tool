# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import SQL
from collections import defaultdict
import itertools
import random


class TreasureTable(models.Model):
    _name = 'treasure.table'

    _order = 'name,id'

    name = fields.Char('Name', required=True)
    table_line_ids = fields.One2many('treasure.table.line', 'table_id', 'Possible Treasures')
    num_pulls = fields.Integer('Rolls', default=1, help='Number of times to roll on the table to generate a hoard.', required=True)

    _sql_constraints = [
        ('check_num_pulls_positive', 'CHECK (num_pulls > 0)',
         'Rolls must be positive.'),
    ]

    average_value = fields.Float('Average Worth', compute='_compute_average_value')

    @api.depends('num_pulls','table_line_ids', 'table_line_ids.res_model_ref', 'table_line_ids.ticket_amount', 'table_line_ids.multiplier')
    def _compute_average_value(self):
        for rec in self:
            if not rec.table_line_ids:
                rec.average_value = 0
                continue
            average_value = rec.num_pulls * sum(line.average_value * line.multiplier * line.ticket_amount for line in rec.table_line_ids) / sum(line.ticket_amount for line in rec.table_line_ids)
            rec.average_value = average_value

    def _check_treasure_recursion(self):
        cr = self._cr
        self.env['treasure.table.line'].flush_model(['table_id', 'res_model_ref'])
        succs = defaultdict(set)  # transitive closure of successors
        preds = defaultdict(set)  # transitive closure of predecessors
        todo, done = set(self.ids), set()
        while todo:
            # retrieve the respective successors of the nodes in 'todo'

            cr.execute(SQL(
                """ SELECT table_id, split_part(res_model_ref,',',2)
                    FROM treasure_table_line
                    WHERE table_id IN %(ids)s
                      AND res_model_ref LIKE %(pattern)s""",
                ids=tuple(todo),
                pattern='treasure.table,%'
            ))
            done.update(todo)
            todo.clear()
            for id1, id2 in cr.fetchall():
                id2 = int(id2)
                # connect id1 and its predecessors to id2 and its successors
                for x, y in itertools.product([id1] + list(preds[id1]),
                                              [id2] + list(succs[id2])):
                    if x == y:
                        return False  # we found a cycle here!
                    succs[x].add(y)
                    preds[y].add(x)
                if id2 not in done:
                    todo.add(id2)
        return True

    def action_treasure_generator(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("treasure_tool.act_treasure_generation")
        action['context'] = {
            'default_treasure_table_id': self.id,
        }
        return action

    def _generate_treasure(self, num_pulls_override=None):
        self.ensure_one()
        if num_pulls_override is not None:
            num_pulls = int(num_pulls_override)
        else:
            num_pulls = self.num_pulls
        result = []
        for _ in range(num_pulls):
            chosen_line = random.choices(self.table_line_ids, weights=self.table_line_ids.mapped('ticket_amount'))[0]
            sub_res = chosen_line.res_model_ref._generate_treasure()
            for entry in sub_res:
                entry['amount'] *= chosen_line.multiplier
            result += sub_res
        return result

class TreasureTableLine(models.Model):
    _name = 'treasure.table.line'

    table_id = fields.Many2one('treasure.table', 'Corresponding Table', ondelete="cascade")

    res_model_ref = fields.Reference(
        selection=[
        ('treasure.coin.hoard', 'Coin'),
        ('treasure.artifact', 'Artifact'),
        ('treasure.table', 'Treasure Table'),
    ],
        string='Record')

    ticket_amount = fields.Integer('Tickets', default=1, help='Number of times this entry is entered into the lottery to determine what appears.', required=True)
    multiplier = fields.Integer(string='Multiplier', default=1, help='', required=True)

    average_value = fields.Float('Average Worth', compute='_compute_average_value')

    _sql_constraints = [
        ('check_ticket_amount_positive', 'CHECK (ticket_amount > 0)',
         'Tickets must be positive.'),
        ('check_multiplier_positive', 'CHECK (multiplier > 0)',
         'Multiplier must be positive.'),
    ]

    @api.constrains('res_model_ref')
    def _check_table_recursion(self):
        if not self.table_id._check_treasure_recursion():
            raise ValidationError(_('Error! You cannot create a recursion of treasure tables.'))

    @api.depends('res_model_ref')
    def _compute_average_value(self):
        for rec in self:
            if rec.res_model_ref and hasattr(rec.res_model_ref,'average_value'):
                rec.average_value = rec.res_model_ref.average_value
            else:
                rec.average_value = 0