# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError
import pydot
from markupsafe import Markup

class ReportPointMap(models.AbstractModel):
    _name = 'report.pointcrawl_tool.report_point_map'
    _description = 'Pointmap Graph View'

    @api.model
    def _get_report_values(self, docids, data=None):
        locations = self.env['point.location'].search([])
        connections = locations.connection_down_ids | locations.connection_up_ids
        graph = pydot.Dot("point_map", graph_type="graph")
        for location in locations:
            graph.add_node(pydot.Node(location.id,label=location.name,color=location.display_color))
        for connection in connections:
            graph.add_edge(pydot.Edge(connection.location_up_id.id,connection.location_down_id.id,color=connection.display_color))
        svg = graph.create(format="svg",prog="fdp").decode()
        return {'svg': Markup(svg)}