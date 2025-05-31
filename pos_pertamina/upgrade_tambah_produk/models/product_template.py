from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    min_allowed_price = fields.Float(string='Harga Minimum')
    max_allowed_price = fields.Float(string='Harga Maksimum')
