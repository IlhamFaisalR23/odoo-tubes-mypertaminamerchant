from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PosManualCalculation(models.Model):
    _name = 'pos.manual.calculation'
    _description = 'Manual Calculation for POS'

    name = fields.Char('Nama Produk', required=True)
    price_unit = fields.Float('Harga Satuan', required=True)
    quantity = fields.Float('Jumlah', required=True)
    total_price = fields.Float('Total Harga', compute='_compute_total_price', store=True)
    saved_to_catalog = fields.Boolean('Disimpan ke Katalog', default=False)
    product_id = fields.Many2one('product.product', string='Produk', readonly=True)

    @api.depends('price_unit', 'quantity')
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.price_unit * record.quantity

    def action_save_to_product_catalog(self):
        for record in self:
            # Validasi input
            if not record.name or record.price_unit <= 0:
                raise ValidationError("Nama produk dan harga harus diisi dengan benar.")

            # Cek apakah produk sudah ada
            existing_product = self.env['product.product'].search([
                ('name', '=', record.name),
                ('list_price', '=', record.price_unit)
            ], limit=1)

            if not existing_product:
                # Buat produk baru jika belum ada
                try:
                    product = self.env['product.product'].create({
                        'name': record.name,
                        'list_price': record.price_unit,
                        'type': 'product',
                        'detailed_type': 'product',
                        'available_in_pos': True,
                        'categ_id': self.env.ref('product.product_category_all').id,
                    })
                    record.product_id = product
                    record.saved_to_catalog = True
                except Exception as e:
                    raise ValidationError(f"Gagal membuat produk: {str(e)}")

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }