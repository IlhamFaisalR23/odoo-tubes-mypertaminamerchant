{
    "name": "POS Custom Input Product Manual",
    "version": "16.0.1.0.0",
    "summary": "POS Custom Input Product Manual",
    "author": "PentaDev",
    "license": "LGPL-3",
    "category": "Point of Sale",
    "depends": ["point_of_sale"],
    "external_dependencies": {},
    "demo": [],
    "data": ["views/res_config_settings_view.xml", "security/ir.model.access.csv"],
    "assets": {
        "point_of_sale.assets": [
            "pos_custom_input_manual/static/src/css/pos.css",
            "pos_custom_input_manual/static/src/js/*.js",
            "pos_custom_input_manual/static/src/xml/*.xml",
        ],
    },
    "installable": True,
    "application": False,
}
