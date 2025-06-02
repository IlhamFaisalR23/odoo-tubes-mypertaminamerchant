{
    'name': 'POS MyPertamina Merchants',
    'version': '1.0',
    'summary': 'POS System for MyPertamina Merchants',
    'category': 'Inventory',
    'author': 'PentaDev',
    'depends': ['stock', 'product', 'point_of_sale', 'base'],
    'post_init_hook': 'post_init_hook',
    'data': [
        'upgrade_pemantauan_stok/views/product_template_views.xml',
        'upgrade_pemantauan_stok/data/forecast_notify_cron.xml',
        'master_data/data/product_category.xml',
        'master_data/data/product_pertamina.xml',
        'upgrade_tambah_produk/views/product_template_view.xml',
        'upgrade_transaction/static/src/xml/receipt_vehicle.xml',
        'upgrade_tambah_produk/views/product_category_restrict_view.xml',
        'upgrade_tambah_produk/security/ir.model.access.csv',
        'upgrade_tambah_produk/security/product_rules.xml',
        'master_data/data/pos_category.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_pertamina/upgrade_transaction/static/src/js/vehicle_prompt.js',
        ],
        'web.assets_backend': [
            'pos_pertamina/upgrade_tambah_produk/static/src/js/category_form_restriction.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
