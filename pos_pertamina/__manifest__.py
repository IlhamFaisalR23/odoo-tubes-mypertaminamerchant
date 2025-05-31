{
    'name': 'POS MyPertamina Merchants',
    'version': '1.0',
    'summary': 'POS System for MyPertamina Merchants',
    'category': 'Inventory',
    'author': 'PentaDev',
    'depends': ['stock', 'product'],
    'data': [
        'upgrade_pemantauan_stok/views/product_template_views.xml',
        'upgrade_pemantauan_stok/data/forecast_notify_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
