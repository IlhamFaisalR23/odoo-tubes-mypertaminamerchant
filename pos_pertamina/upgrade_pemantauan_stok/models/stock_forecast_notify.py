from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def notify_forecast_low(self):
        threshold = 0.05  # batas harian
        products = self.search([('forecast_value', '<=', threshold)])
        for product in products:
            product.message_post(
                body=f"⚠️ Perhatian! Forecast stok '{product.name}' menipis: {product.forecast_value:.2f} per hari"
            )
