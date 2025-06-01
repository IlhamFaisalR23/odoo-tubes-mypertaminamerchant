odoo.define("pos_edit_order_line.ManualCalculationPopup", function (require) {
  "use strict";

  const { useState } = owl;
  const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
  const Registries = require("point_of_sale.Registries");
  const rpc = require("web.rpc");

  class ManualCalculationPopup extends AbstractAwaitablePopup {
    setup() {
      super.setup();
      this.state = useState({
        name: "",
        price_unit: 0,
        quantity: 1,
        manualCalcId: null,
      });
    }

    async saveToProductCatalog() {
      const { name, price_unit } = this.state;

      if (typeof name !== "string" || name.trim() === "" || price_unit <= 0) {
        this.showPopup("ErrorPopup", {
          title: "Validasi Gagal",
          body: "Harap isi nama produk dan harga dengan benar",
        });
        return;
      }

      try {
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
            },
          ],
        });

        if (this.state.manualCalcId) {
          await rpc.query({
            model: "pos.manual.calculation",
            method: "write",
            args: [[this.state.manualCalcId], { saved_to_catalog: true }],
          });
        }

        this.showPopup("ConfirmPopup", {
          title: "Berhasil",
          body: `Produk ${name} telah disimpan ke katalog`,
        });
      } catch (error) {
        console.error("Error menyimpan ke katalog:", error);
        this.showPopup("ErrorPopup", {
          title: "Kesalahan",
          body: error.message || "Gagal menyimpan produk ke katalog",
        });
      }
    }

    confirm() {
      const { name, price_unit, quantity } = this.state;

      if (
        typeof name !== "string" ||
        name.trim() === "" ||
        price_unit <= 0 ||
        quantity <= 0
      ) {
        this.showPopup("ErrorPopup", {
          title: "Validasi Gagal",
          body: "Harap isi semua field dengan benar",
        });
        return;
      }

      console.log("Payload konfirmasi:", { name, price_unit, quantity });

      this.env.posbus.trigger("close-popup", {
        popupId: this.props.id,
        response: {
          confirmed: true,
          payload: { name: name.trim(), price_unit, quantity },
        },
      });
    }
  }

  ManualCalculationPopup.template = "ManualCalculationPopup";
  ManualCalculationPopup.defaultProps = {
    confirmText: "Konfirmasi",
    cancelText: "Batal",
  };

  Registries.Component.add(ManualCalculationPopup);

  return ManualCalculationPopup;
});
