# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import math
from datetime import timedelta

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    # Tambahan field: forecast_per_day (angka rata‐rata keluar per hari)
    forecast_per_day = fields.Float(
        string='Forecast per Hari',
        help='Rata‐rata kebutuhan harian berdasarkan 30 hari terakhir (otomatis dihitung).',
        compute='_compute_forecast', store=True)

    # Jika ingin user override minimal, tambahkan field threshold_override
    threshold_override = fields.Boolean('Override Threshold Manual',
                                        default=False)

    @api.depends('product_id', 'product_id.uom_id', 'warehouse_id')
    def _compute_forecast(self):
        """
        Contoh sederhana: hitung total penjualan 30 hari terakhir dibagi 30
        (diimplementasikan dengan logic sederhana dari stock move).
        """
        for orderpoint in self:
            product = orderpoint.product_id
            if not product:
                orderpoint.forecast_per_day = 0.0
                continue

            # Cari semua stock.move keluar (outgoing) untuk produk ini 30 hari ke belakang (per warehouse location)
            domain = [
                ('product_id', '=', product.id),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '!=', 'internal'),
                ('date', '>=', (fields.Datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')),
            ]
            moves = self.env['stock.move'].search(domain)
            total_qty = sum(moves.mapped('product_uom_qty'))
            # Rata2 per hari
            orderpoint.forecast_per_day = total_qty / 30 if total_qty else 0.0

    def _cron_check_orderpoint(self):
        """
        Cron job yang nanti dijalankan secara berkala (misal: setiap jam).
        Ketika stok aktual <= minimum_qty, dan reordering aktif:
           - Buat draft purchase.order,
             atau
           - Buat notifikasi/entry di menu Reordering
        """
        Orderpoint = self.env['stock.warehouse.orderpoint']
        now = fields.Datetime.now()
        # Ambil semua orderpoint aktif
        orderpoints = Orderpoint.search([('active', '=', True)])
        for op in orderpoints:
            # Ambil qty_on_hand terkini untuk produk di lokasi warehouse
            stock_qty = op._get_real_time_stock()  # contoh: fungsi Odoo default
            # Jika override manual, kita skip logika otomatis
            if op.threshold_override:
                continue

            if stock_qty <= op.product_min_qty:
                # Hitung qty yang perlu dibuat (misal: target = max_qty - current)
                needed_qty = op.product_max_qty - stock_qty if op.product_max_qty > stock_qty else 0
                if needed_qty > 0:
                    # Buat draft purchase order
                    self._create_draft_purchase(op, needed_qty)

    def _get_real_time_stock(self):
        """
        Contoh fungsi sederhana untuk hitung stok yang tersedia pada warehouse/ lokasi ini.
        """
        quant = self.env['stock.quant']
        domain = [
            ('product_id', '=', self.product_id.id),
            ('location_id', 'child_of', self.location_id.id),
        ]
        quants = quant.search(domain)
        return sum(quants.mapped('quantity'))

    def _create_draft_purchase(self, orderpoint, qty):
        """
        Buat draft purchase.order dengan satu baris product.
        Jika sudah ada draft PO untuk supplier yang sama+product yang sama,
        bisa kita tambah kuantitas di PO yang existing atau bikin baru.
        """
        # Kita gunakan supplier info dari product.supplierinfo (bila ada)
        supplier_info = orderpoint.product_id.seller_ids and orderpoint.product_id.seller_ids[0]
        if not supplier_info:
            # Jika tidak ada info supplier, skip atau raise warning
            _logger = self.env['ir.logging']
            _logger.create({
                'name': 'Auto Purchase Error',
                'type': 'server',
                'dbname': self.env.cr.dbname,
                'level': 'warning',
                'message': _('Tidak ada supplier untuk produk %s, otomatis PO gagal dibuat.') % orderpoint.product_id.display_name,
            })
            return

        # Cek apakah sudah ada draft PO (state='draft') untuk supplier & produk yang sama
        domain = [
            ('state', '=', 'draft'),
            ('partner_id', '=', supplier_info.name.id),
        ]
        existing_po = self.env['purchase.order'].search(domain, limit=1)
        if existing_po:
            # Tambah baris baru atau update kuantitas jika sdh ada product_id
            pol = existing_po.order_line.filtered(lambda l: l.product_id.id == orderpoint.product_id.id)
            if pol:
                pol.product_qty += qty
            else:
                existing_po.write({
                    'order_line': [(0, 0, {
                        'product_id': orderpoint.product_id.id,
                        'name': orderpoint.product_id.display_name,
                        'product_qty': qty,
                        'product_uom': orderpoint.product_id.uom_id.id,
                        'date_planned': fields.Date.today(),
                        'price_unit': supplier_info.price,
                        'taxes_id': [(6, 0, [tax.id for tax in supplier_info.product_taxes_id])],
                    })]
                })
        else:
            # Buat PO baru
            po_vals = {
                'partner_id': supplier_info.name.id,
                'date_order': fields.Date.today(),
                'order_line': [(0, 0, {
                    'product_id': orderpoint.product_id.id,
                    'name': orderpoint.product_id.display_name,
                    'product_qty': qty,
                    'product_uom': orderpoint.product_id.uom_id.id,
                    'date_planned': fields.Date.today(),
                    'price_unit': supplier_info.price,
                    'taxes_id': [(6, 0, [tax.id for tax in supplier_info.product_taxes_id])],
                })],
            }
            self.env['purchase.order'].create(po_vals)
