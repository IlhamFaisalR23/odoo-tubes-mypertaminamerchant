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
        'master_data/data/product_category.xml',
        'master_data/data/product_pertamina.xml',
        'upgrade_tambah_produk/views/product_template_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
