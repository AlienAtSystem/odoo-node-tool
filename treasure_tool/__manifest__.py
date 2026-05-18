# -*- coding: utf-8 -*-
{
    'application': True,
    'author': 'AlienAtSystem',
    'category': 'TTRPG',
    'depends': ['web'],
    'external_dependencies': {
        'python': ['numpy']
    },
    'description': u"""Tool to handle RPG treasure and generate hoards from it.""",
    'images': ['static/description/thumbnail.png'],
    'license': 'GPL-3',
    'name': 'Treasure Tool',
    'summary': 'Implements Treasure Tables',
    'version': '1.0.0',
    'data': [
        'security/ir.model.access.csv',
        'views/treasure_table_views.xml',
        'views/treasure_coin_views.xml',
        'views/treasure_artifact_views.xml',
        'views/menu_views.xml',
        'wizards/treasure_generation_wizard.xml',
        'data/coin_data.xml',
    ],
}