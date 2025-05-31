{
    'name': 'POS MyPertamina Merchants',
    'version': '1.0',
    'summary': 'POS System for MyPertamina Merchants',
    'category': 'Inventory',
    'author': 'PentaDev',
    'depends': ['stock', 'product', 'point_of_sale'],
    'data': [
        'upgrade_pemantauan_stok/views/product_template_views.xml',
        'upgrade_pemantauan_stok/data/forecast_notify_cron.xml',
        'upgrade_transaction/static/src/xml/receipt_vehicle.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_pertamina/upgrade_transaction/static/src/js/vehicle_prompt.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
