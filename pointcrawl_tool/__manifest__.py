# -*- coding: utf-8 -*-
{
    'application': True,
    'author': 'AlienAtSystem',
    'category': 'TTRPG',
    'depends': [],
    'description': u"""Tool to design and run Pointcrawl Adventures.""",
    'images': ['static/description/thumbnail.png'],
    'license': 'GPL-3',
    'name': 'Pointcrawl Tool',
    'summary': 'Implements Pointcrawl Maps',
    'version': '1.0.0',
    'data': [
        'security/ir.model.access.csv',
        'views/connection_views.xml',
        'views/area_views.xml',
        'views/location_views.xml',
        'views/report_views.xml',
        'views/menu_views.xml',
        'report/report_point_map.xml',
    ],
}