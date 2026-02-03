{
    'name': 'Manufacturing Partial Production',
    'version': '19.0.0.0',
    'depends': ['mrp', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/partial_production_view.xml',
        'wizard/view_partially_production_warning_form.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mrp_partial_production/static/src/partial_production_shop_floor/partial_production_shop_floor.xml',
            'mrp_partial_production/static/src/partial_production_shop_floor/partial_production_shop_floor.js',
        ],
    },
}