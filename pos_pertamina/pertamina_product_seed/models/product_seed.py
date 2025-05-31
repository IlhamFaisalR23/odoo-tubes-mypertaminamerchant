from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class PertaminaProductSeeder(models.AbstractModel):
    _name = 'pertamina.product.seeder'
    _description = 'Seeder for Pertamina BBM Products'

    @api.model
    def _seed_pertamina_products(self):
        # Daftar produk BBM Pertamina
        pertamina_products = [
            {'name': 'Pertalite',        'default_code': 'PRTL', 'list_price': 10000},
            {'name': 'Pertamax',         'default_code': 'PRTX', 'list_price': 12500},
            {'name': 'Pertamax Turbo',   'default_code': 'PRTM', 'list_price': 14500},
            {'name': 'Solar',            'default_code': 'SOLR', 'list_price': 6800},
            {'name': 'Dexlite',          'default_code': 'DEXL', 'list_price': 13500},
        ]

        Product = self.env['product.product']
        Category = self.env['product.category']
        bbm_category = Category.search([('name', '=', 'BBM')], limit=1)
        if not bbm_category:
            bbm_category = Category.create({'name': 'BBM'})
            _logger.info("Created product category: BBM")

        for prod in pertamina_products:
            existing = Product.search([('default_code', '=', prod['default_code'])], limit=1)
            if not existing:
                Product.create({
                    'name': prod['name'],
                    'default_code': prod['default_code'],
                    'list_price': prod['list_price'],
                    'type': 'product',
                    'categ_id': bbm_category.id,
                    'uom_id': self.env.ref('uom.product_uom_litre').id,
                    'uom_po_id': self.env.ref('uom.product_uom_litre').id,
                })
                _logger.info(f"Created Pertamina product: {prod['name']}")
            else:
                _logger.info(f"Pertamina product already exists: {prod['name']}")

    @api.model
    def init(self):
        self._seed_pertamina_products()
