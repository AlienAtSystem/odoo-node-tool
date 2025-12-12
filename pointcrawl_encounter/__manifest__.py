# -*- coding: utf-8 -*-
{
    'author': 'AlienAtSystem',
    'category': 'TTRPG',
    'depends': ['pointcrawl_tool', 'encounter_tool'],
    'description': u"""Integrates Encounters into Pointcrawls.""",
    'images': ['static/description/thumbnail.png'],
    'license': 'GPL-3',
    'name': 'Pointcrawl Encounters',
    'summary': 'Integrates Encounters into Pointcrawls',
    'version': '1.0.0',
    'data': [
        'security/ir.model.access.csv',
        'views/pointcrawl_views.xml',
    ],
    'auto_install': True,
}