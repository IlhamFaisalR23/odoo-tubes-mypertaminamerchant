from odoo import models, fields, api
from datetime import timedelta

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    forecast_value = fields.Float(
        string="Forecast", compute="_compute_forecast_value", store=True, help="Perkiraan jumlah penjualan per hari selama 30 hari terakhir."
    )

    @api.depends('qty_available')
    def _compute_forecast_value(self):
        for rec in self:
            days = 30
            date_from = fields.Date.today() - timedelta(days=days)
            moves = self.env['stock.move'].search([
                ('product_id', '=', rec.id),
                ('date', '>=', date_from),
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '=', 'customer'),  # hanya yang keluar ke customer
            ])
            total_out = sum(move.product_uom_qty for move in moves)
            rec.forecast_value = total_out / days if days else 0
