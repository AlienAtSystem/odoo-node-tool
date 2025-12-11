# -*- coding: utf-8 -*-
{
    'application': True,
    'author': 'AlienAtSystem',
    'category': 'TTRPG',
    'depends': [],
    'description': u"""Tool to manage a bestiary and automatically generate encounters from it.""",
    'images': ['static/description/thumbnail.png'],
    'license': 'GPL-3',
    'name': 'Bestiary Tool',
    'summary': 'Implements Bestiaries and Encounters',
    'version': '1.0.0',
    'data': [
        'security/ir.model.access.csv',
        'data/lanchester_data.xml',
        'views/bestiary_views.xml',
        'views/encounter_views.xml',
        'views/menu_views.xml',
        'wizards/encounter_generation_wizard.xml',
    ],
}