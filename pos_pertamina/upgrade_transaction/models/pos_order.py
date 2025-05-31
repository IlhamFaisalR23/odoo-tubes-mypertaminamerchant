from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    pertamina_vehicle_type = fields.Char(
        string='Jenis Kendaraan',
        help='Jenis kendaraan untuk transaksi Pertamina'
    )
    
    @api.model
    def _order_fields(self, ui_order):
        """Override untuk menambahkan field pertamina_vehicle_type"""
        order_fields = super()._order_fields(ui_order)
        
        # Tambahkan vehicle type dari frontend
        if 'pertamina_vehicle_type' in ui_order:
            order_fields['pertamina_vehicle_type'] = ui_order['pertamina_vehicle_type']
            _logger.info(f"Saving vehicle type: {ui_order['pertamina_vehicle_type']}")
        
        return order_fields