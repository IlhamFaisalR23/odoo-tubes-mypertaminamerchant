from .upgrade_tambah_produk.models.product_images import update_product_images

def post_init_hook(cr, registry):
    update_product_images(cr, registry)
