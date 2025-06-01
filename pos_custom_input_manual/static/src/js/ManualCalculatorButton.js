odoo.define("pos_edit_order_line.ManualCalculationButton", function (require) {
  "use strict";

  const PosComponent = require("point_of_sale.PosComponent");
  const ProductScreen = require("point_of_sale.ProductScreen");
  const { useListener } = require("@web/core/utils/hooks");
  const Registries = require("point_of_sale.Registries");
  const rpc = require("web.rpc");
  const { _lt } = require("web.core");

  class ManualCalculationButton extends PosComponent {
    setup() {
      super.setup();
      useListener("click", this.onClick);
    }

    async onClick() {
      const { confirmed, payload } = await this.showPopup(
        "ManualCalculationPopup",
        { title: this.env._t("Hitung Manual") }
      );

      if (confirmed && payload) {
        await this.addManualProduct(payload);
      }
    }

    async addManualProduct(payload) {
      const { name, price_unit, quantity } = payload;

      try {
        // Langkah 1: Buat produk di tabel product.product melalui RPC
        const productId = await rpc.query({
          model: "product.product",
          method: "create",
          args: [
            {
              name: name,
              list_price: price_unit,
              type: "product",
              detailed_type: "product",
              available_in_pos: true,
              taxes_id: [], // Pastikan pajak kosong atau sesuai kebutuhan
              pos_categ_id: false, // Kategori POS default
            },
          ],
        });

        // Langkah 2: Ambil UoM default dari POS config
        const defaultUomId = this.env.pos.units_by_id[1]
          ? 1
          : Object.keys(this.env.pos.units_by_id)[0];

        // Langkah 3: Buat objek produk untuk POS dengan product_id yang valid
        const tempProduct = {
          id: productId, // Gunakan ID produk yang baru dibuat
          display_name: name,
          name: name,
          lst_price: price_unit,
          price: price_unit,
          type: "product",
          tracking: "none",
          uom_id: defaultUomId,
          taxes_id: [],
          pos_categ_id: false,
          get_price: () => price_unit,
          get_unit: () =>
            this.env.pos.units_by_id[defaultUomId] || { name: "Unit" },
        };

        // Langkah 4: Tambahkan produk ke database lokal POS
        this.env.pos.db.add_products([tempProduct]);

        // Langkah 5: Tambahkan ke pesanan
        const order = this.env.pos.get_order();
        const orderline = order.add_product(tempProduct, {
          quantity: quantity,
          price: price_unit,
        });

        if (orderline) {
          orderline.get_unit = () =>
            this.env.pos.units_by_id[defaultUomId] || { name: "Unit" };
          orderline.get_unit_price = () => price_unit;
        }

        // Langkah 6: Simpan ke database manual calculation (opsional)
        const manualCalcId = await rpc.query({
          model: "pos.manual.calculation",
          method: "create",
          args: [
            {
              name: name,
              price_unit: price_unit,
              quantity: quantity,
            },
          ],
        });

        return manualCalcId;
      } catch (error) {
        console.error("Error menambahkan produk manual:", error);
        this.showPopup("ErrorPopup", {
          title: "Kesalahan",
          body: error.message || "Gagal menambahkan produk manual",
        });
      }
    }
  }

  // Override metode add_product untuk menangani produk manual
  const originalAddProduct = ProductScreen.prototype.add_product;
  ProductScreen.prototype.add_product = function (product, options) {
    if (product.id && typeof product.id === "number") {
      // Pastikan ID adalah integer
      product.get_unit = () =>
        this.env.pos.units_by_id[product.uom_id] || { name: "Unit" };
      product.get_price = () => options.price || product.lst_price;
    }
    return originalAddProduct.call(this, product, options);
  };

  ManualCalculationButton.template = "ManualCalculationButton";

  ProductScreen.addControlButton({
    component: ManualCalculationButton,
    condition: function () {
      return this.env.pos.config.allow_manual_calculation;
    },
  });

  Registries.Component.add(ManualCalculationButton);

  return ManualCalculationButton;
});
