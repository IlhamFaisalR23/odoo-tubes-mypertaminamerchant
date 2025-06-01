from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def create(self, vals):
        if (self.env.context.get('module_install', False) or 
            self.env.context.get('install_mode', False) or
            self.env.context.get('loading', False)):
            return super().create(vals)

        user = self.env.user
        non_pertamina = self.env.ref('pos_pertamina.product_category_non_pertamina', raise_if_not_found=False)

        if not user.has_group('base.group_system'):
            raise UserError(_("Anda tidak diizinkan membuat kategori produk."))

        parent_id = vals.get('parent_id')
        if not parent_id:
            raise UserError(_("Admin hanya boleh membuat subkategori dari 'Non-Pertamina'."))

        parent_category = self.env['product.category'].browse(parent_id)
        if not non_pertamina or not parent_category._is_child_of(non_pertamina):
            raise UserError(_("Admin hanya boleh membuat subkategori dari kategori 'Non-Pertamina'."))

        return super().create(vals)

    def write(self, vals):
        if (self.env.context.get('module_install', False) or 
            self.env.context.get('install_mode', False) or
            self.env.context.get('loading', False)):
            return super().create(vals)
        
        user = self.env.user
        pertamina_root = self.env.ref('pos_pertamina.product_category_pertamina', raise_if_not_found=False)

        if not user.has_group('base.group_system'):
            raise UserError(_("Anda tidak diizinkan mengubah kategori produk."))

        for rec in self:
            if pertamina_root and rec._is_child_of(pertamina_root):
                raise UserError(_("Kategori Pertamina tidak boleh diubah."))

        return super().write(vals)

    def unlink(self):
        if (self.env.context.get('module_install', False) or 
            self.env.context.get('install_mode', False) or
            self.env.context.get('loading', False)):
            return super().create(vals)
        
        user = self.env.user
        pertamina_root = self.env.ref('pos_pertamina.product_category_pertamina', raise_if_not_found=False)

        if not user.has_group('base.group_system'):
            raise UserError(_("Anda tidak diizinkan menghapus kategori produk."))

        for rec in self:
            if pertamina_root and rec._is_child_of(pertamina_root):
                raise UserError(_("Kategori Pertamina tidak boleh dihapus."))

        return super().unlink()

    def _is_child_of(self, parent):
        if isinstance(parent, int):
            parent = self.env['product.category'].browse(parent)
        current = self
        while current:
            if current.id == parent.id:
                return True
            current = current.parent_id
        return False
