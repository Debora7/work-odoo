# -*- coding: utf-8 -*-
{
    'name':'Smart Contract',
    'description': "",
    'version':'19.0.0.1.0',
    'author':'Dakai SOFT',
    'data': [
        'security/contract_security.xml',
        'security/ir.model.access.csv',
    
        'views/menus.xml',
        'views/smart_contract_view.xml',
        'views/smart_contract_template_view.xml',
        'views/smart_contract_template_element.view.xml',
    ],
    'depends': [
        'base', 
        'portal',
        'website',
        'purchase', 
        'account',
        'sales_team',
    ],
    'category': 'Sales',
    'installable': True,
    'application': True,
    'auto_install': False,
}
