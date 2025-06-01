import base64
import os
import logging
import xml.etree.ElementTree as ET
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def update_product_images(cr, registry):
    
    env = api.Environment(cr, SUPERUSER_ID, {})

    module_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.dirname(os.path.dirname(module_path))

    image_folder = os.path.join(base_path, 'static', 'img')
    xml_file = os.path.join(base_path, 'data', 'product_pertamina.xml')

    if not os.path.exists(xml_file):
        _logger.error(f"XML file not found: {xml_file}")
        return

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for record in root.findall("record"):
        xml_id = record.attrib.get("id")
        if not xml_id:
            continue

        data = env['ir.model.data'].search([
            ('model', '=', 'product.template'),
            ('module', '=', 'pos_pertamina'),
            ('name', '=', xml_id)
        ], limit=1)

        if data and data.res_id:
            product = env['product.template'].browse(data.res_id)
            img_path = os.path.join(image_folder, f"{xml_id}.jpeg")

            if os.path.exists(img_path):
                with open(img_path, "rb") as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data)

                product.with_context(bypass_image_update=True).write({'image_1920': img_base64})
                _logger.info(f"Image updated: {xml_id} → {product.name}")
            else:
                _logger.warning(f"Image not found: {img_path}")
        else:
            _logger.warning(f"Product not found for xml_id={xml_id}")
