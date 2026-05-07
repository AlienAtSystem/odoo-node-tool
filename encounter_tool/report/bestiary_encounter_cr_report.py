# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


class ReportAccountHashIntegrity(models.AbstractModel):
    _name = 'report.encounter_tool.encounter_cr_report'
    _description = 'Compares encounters according to their amount-weighed challenge rating.'

    @api.model
    def _get_report_values(self, docids, data=None):
        encounters = self.env['bestiary.encounter.table'].search([])
        cr_param, n_param = self.env['bestiary.encounter.wizard']._get_lanchester_parameters()
        if n_param is False:
            raise UserError("The Lanchester Parameters are not set correctly.")
        report_lines = [self._get_report_line(encounter, n_param) for encounter in encounters]
        averages = {}
        if report_lines:
            averages = self._process_averages(report_lines, cr_param, n_param)
            self._sort_lines(report_lines)
        return {'lines': report_lines, **averages}

    @api.model
    def _get_report_line(self, encounter, n_param):
        return {
            'name': encounter.name,
            'average_cr': encounter.average_cr,
            'number_appearing_min': encounter.number_appearing_min,
            'number_appearing_max': encounter.number_appearing_max,
            'num_entries': len(encounter.table_line_ids),
            'number_appearing_average': ((encounter.number_appearing_min ** n_param + encounter.number_appearing_max ** n_param) / 2) ** (1/n_param),
        }

    @api.model
    def _process_averages(self, report_lines, cr_param, n_param):
        num_total_average = sum(entry['number_appearing_average'] for entry in report_lines) / len(report_lines)
        cr_total_average = sum(entry['average_cr'] for entry in report_lines) / len(report_lines)
        for line in report_lines:
            line['qualified_cr'] = line['average_cr'] * (line['number_appearing_average'] / num_total_average) ** (n_param / cr_param)
        cr_qualified_average = sum(entry['qualified_cr'] for entry in report_lines) / len(report_lines)
        return {
            'num_total_average': num_total_average,
            'cr_total_average': cr_total_average,
            'cr_qualified_average': cr_qualified_average,
        }

    @api.model
    def _sort_lines(self, lines):
        lines.sort(key=lambda line: line['qualified_cr'], reverse=False)