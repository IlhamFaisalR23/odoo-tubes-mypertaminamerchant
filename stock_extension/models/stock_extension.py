from odoo import models, fields, api
from datetime import timedelta

class ProductProduct(models.Model):
    _inherit = 'product.product'
    forecast_value = fields.Float(string="Forecast", compute="_compute_forecast_value")

    def _compute_forecast_value(self):
        for product in self:
            days = 30
            date_from = fields.Date.today() - timedelta(days=days)
            moves = self.env['stock.move'].search([
                ('product_id', '=', product.id),
                ('date', '>=', date_from),
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'internal')
            ])
            total_out = sum(move.product_uom_qty for move in moves)
            product.forecast_value = total_out / days if days else 0

class OrderPoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    def check_reorder_notify(self):
        for op in self.search([]):
            if op.product_id.qty_available <= op.product_min_qty:
                op.message_post(body=f"⚠️ Stok produk '{op.product_id.display_name}' menipis!")

