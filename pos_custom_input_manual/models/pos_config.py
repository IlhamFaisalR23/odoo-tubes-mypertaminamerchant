from odoo import fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    allow_manual_calculation = fields.Boolean(
        string="Allow Manual Calculation",
        default=True,
    )