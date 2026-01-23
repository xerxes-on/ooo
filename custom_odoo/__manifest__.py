# -*- coding: utf-8 -*-
{
    'name': 'Custom Odoo',
    'version': '18.0.1.0.0',
    'category': 'Customizations',
    'summary': 'Custom Odoo Module Template',
    'description': """
Custom Odoo Module
==================
A template module for custom Odoo development.

Features:
---------
* Standard module structure
* Sample model and views
* Security configuration
* Development guidelines
    """,
    'author': 'DearERP',
    'website': 'https://dearerp.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/sample_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
