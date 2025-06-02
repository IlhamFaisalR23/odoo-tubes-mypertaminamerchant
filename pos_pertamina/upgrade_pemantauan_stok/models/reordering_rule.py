from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StockReorderForecastRule(models.Model):
    _name = 'stock.reorder.forecast.rule'
    _description = 'Reordering Rule with Forecast'

    name = fields.Char(string='Rule Name', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    min_qty = fields.Float(string='Minimum Quantity', required=True, default=0.0)
    max_qty = fields.Float(string='Maximum Quantity', required=True, default=0.0)
    forecast_threshold = fields.Float(string='Forecast Threshold', required=True, default=0.0,
                                      help='Jumlah perkiraan minimum sebelum reorder trigger aktif')
    auto_trigger = fields.Boolean(string='Auto Trigger', default=True,
                                  help='Jika aktif, sistem akan otomatis membuat draft purchase order')

    @api.constrains('min_qty', 'max_qty')
    def _check_qty(self):
        for rule in self:
            if rule.min_qty < 0 or rule.max_qty < 0:
                raise ValidationError('Quantity tidak boleh negatif.')
            if rule.min_qty > rule.max_qty:
                raise ValidationError('Minimum quantity tidak boleh lebih besar dari maksimum quantity.')

    def check_and_create_reorder(self):
        """
        Fungsi ini bisa dijalankan via scheduler untuk otomatis cek dan buat PO.
        """
        PurchaseOrder = self.env['purchase.order']
        for rule in self:
            product = rule.product_id
            current_qty = product.qty_available
            forecast = self._get_product_forecast(product)

            if rule.auto_trigger and current_qty <= rule.min_qty and forecast >= rule.forecast_threshold:
                # Cek apakah sudah ada draft PO untuk produk ini untuk menghindari duplikasi
                existing_po = PurchaseOrder.search([
                    ('state', '=', 'draft'),
                    ('order_line.product_id', '=', product.id)
                ], limit=1)
                if not existing_po:
                    supplier = self._get_default_supplier(product)
                    if not supplier:
                        continue
                    po = PurchaseOrder.create({
                        'partner_id': supplier.id,
                        'order_line': [(0, 0, {
                            'product_id': product.id,
                            'product_qty': rule.max_qty - current_qty,
                            'price_unit': product.standard_price,
                            'name': product.name,
                        })],
                    })
                    self.env.user.notify_info(message=f"Draft Purchase Order dibuat untuk {product.name}")

    def _get_product_forecast(self, product):
        """
        Contoh logika forecast sederhana.
        Bisa diintegrasikan dengan data penjualan historis di masa depan.
        """
        # Contoh: forecast 30 hari ke depan rata-rata penjualan harian dikali 30
        sales_data = self.env['sale.order.line'].search([
            ('product_id', '=', product.id),
            ('order_id.state', 'in', ['sale', 'done']),
            ('order_id.date_order', '>=', fields.Date.today().replace(day=1)),
        ])
        if not sales_data:
            return 0.0
        total_qty = sum(line.product_uom_qty for line in sales_data)
        days_count = (fields.Date.today() - fields.Date.today().replace(day=1)).days + 1
        avg_daily = total_qty / days_count if days_count else 0
        return avg_daily * 30  # forecast 30 hari

    def _get_default_supplier(self, product):
        """
        Ambil supplier default produk jika ada.
        """
        supplierinfo = product.seller_ids and product.seller_ids[0]
        if supplierinfo:
            return supplierinfo.name
        return False
