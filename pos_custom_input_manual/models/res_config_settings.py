from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_allow_manual_calculation = fields.Boolean(
        related="pos_config_id.allow_manual_calculation",
        readonly=False,
        string="Manual Calculation",
    )