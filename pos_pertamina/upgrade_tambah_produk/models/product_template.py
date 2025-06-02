from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    min_allowed_price = fields.Float(string='Harga Minimum')
    max_allowed_price = fields.Float(string='Harga Maksimum')
    is_pertamina_category = fields.Boolean(compute='_compute_is_pertamina_category')

    @api.depends('categ_id')
    def _compute_is_pertamina_category(self):
        if (self.env.context.get('module_install', False) or 
            self.env.context.get('install_mode', False) or
            self.env.context.get('loading', False)):
            return

        pertamina_cat = self.env.ref('pos_pertamina.product_category_pertamina', raise_if_not_found=False)
        for rec in self:
            rec.is_pertamina_category = (
                pertamina_cat and rec.categ_id and (
                    rec.categ_id == pertamina_cat or rec.categ_id._is_child_of(pertamina_cat)
                )
            )

    @api.constrains('categ_id')
    def _check_pertamina_category(self):
        if (self.env.context.get('module_install', False) or 
            self.env.context.get('install_mode', False) or
            self.env.context.get('loading', False)):
            return
        
        pertamina_cat = self.env.ref('pos_pertamina.product_category_pertamina', raise_if_not_found=False)
        if not pertamina_cat:
            return

        for rec in self:
            if rec.categ_id and (rec.categ_id == pertamina_cat or rec.categ_id._is_child_of(pertamina_cat)):
                raise UserError("Anda tidak diizinkan menggunakan kategori Pertamina.")

    @api.model
    def create(self, vals):
        if (self.env.context.get('module_install', False) or 
            self.env.context.get('install_mode', False) or
            self.env.context.get('loading', False)):
            return super().create(vals)

        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Anda tidak diizinkan membuat produk. Hubungi administrator."))

        pertamina_cat = self.env.ref('pos_pertamina.product_category_pertamina', raise_if_not_found=False)
        categ_id = vals.get('categ_id')
        if pertamina_cat and categ_id:
            category = self.env['product.category'].browse(categ_id)
            if category == pertamina_cat or category._is_child_of(pertamina_cat):
                raise UserError(_("Anda tidak diperbolehkan membuat produk dengan kategori Pertamina."))

        return super().create(vals)

    def write(self, vals):
        if (self.env.context.get('module_install', False) or 
            self.env.context.get('install_mode', False) or
            self.env.context.get('loading', False) or
            self.env.context.get('bypass_image_update', False)):
            return super().write(vals)

        is_admin = self.env.user.has_group('base.group_system')
        pertamina_cat = self.env.ref('pos_pertamina.product_category_pertamina', raise_if_not_found=False)

        for record in self:
            is_pertamina = pertamina_cat and (record.categ_id == pertamina_cat or record.categ_id._is_child_of(pertamina_cat))

            if is_pertamina:
                if not is_admin:
                    forbidden_fields = set(vals.keys()) - {'qty_available'}
                    if forbidden_fields:
                        raise UserError(_("Anda hanya diizinkan mengubah stok untuk produk kategori Pertamina."))
                    else:
                        allowed_fields = {'list_price', 'qty_available', 'sale_ok', 'available_in_pos'}

                        if vals.get('available_in_pos') is True:
                            allowed_fields |= {'pos_category_id', 'to_weight', 'price', 'barcode'}

                        forbidden_fields = set(vals.keys()) - allowed_fields

                        if forbidden_fields:
                            raise UserError(_("Admin hanya diizinkan mengubah harga jual, stok, opsi menjual, dan field POS tertentu untuk produk kategori Pertamina."))

                        if 'list_price' in vals:
                            new_price = vals['list_price']
                            min_price = record.min_allowed_price
                            max_price = record.max_allowed_price
                            if (min_price is not None and new_price < min_price) or (max_price is not None and new_price > max_price):
                                raise UserError(_(
                                    "Harga jual produk kategori Pertamina harus antara %s dan %s."
                                ) % (min_price or 'tidak ditentukan', max_price or 'tidak ditentukan'))

            else:
                if 'list_price' in vals and is_pertamina is False and not is_admin:
                    raise UserError(_("Hanya admin yang boleh mengubah harga jual produk."))

        return super().write(vals)

    def unlink(self):
        if (self.env.context.get('module_install', False) or 
            self.env.context.get('install_mode', False) or
            self.env.context.get('loading', False)):
            return super().unlink()
            
        pertamina_cat = self.env.ref('pos_pertamina.product_category_pertamina', raise_if_not_found=False)
        for rec in self:
            if pertamina_cat and rec.categ_id and (rec.categ_id == pertamina_cat or rec.categ_id._is_child_of(pertamina_cat)):
                raise UserError(_("Produk dengan kategori Pertamina tidak boleh dihapus, baik oleh admin maupun user biasa."))
        
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Anda tidak diizinkan menghapus produk. Hubungi administrator."))
        
        return super().unlink()