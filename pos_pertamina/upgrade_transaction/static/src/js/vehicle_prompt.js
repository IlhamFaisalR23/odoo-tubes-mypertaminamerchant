odoo.define("upgrade_transaction.vehicle_prompt", function (require) {
  ("use strict");

  const ProductScreen = require("point_of_sale.ProductScreen");
  const Registries = require("point_of_sale.Registries");
  const { Order } = require("point_of_sale.models");

  // Extend ProductScreen
  const CustomProductScreen = (ProductScreen) =>
    class extends ProductScreen {
      async _onClickPay() {
        const order = this.env.pos.get_order();

        if (!order) {
          return super._onClickPay();
        }

        // Cek apakah ada produk Pertamina
        const hasPertaminaProduct = order.get_orderlines().some((line) => {
          const product = line.get_product();
          if (!product || !product.pos_categ_id) return false;

          // Cek nama kategori produk
          const categoryName = product.pos_categ_id[1] || "";
          return categoryName.toLowerCase().includes("pertamina");
        });

        console.log("Has Pertamina Product:", hasPertaminaProduct); // Debug
        console.log("Current Vehicle Type:", order.pertamina_vehicle_type); // Debug

        // Tampilkan popup jika ada produk Pertamina dan belum ada vehicle type
        if (hasPertaminaProduct && !order.pertamina_vehicle_type) {
          console.log("Showing vehicle selection popup...");

          const { confirmed, payload } = await this.showPopup(
            "SelectionPopup",
            {
              title: "Pilih Jenis Kendaraan",
              body: "Silakan pilih jenis kendaraan untuk transaksi Pertamina.",
              list: [
                { id: "motorcycle", label: "Motorcycle", item: "Motorcycle" },
                { id: "car", label: "Car", item: "Car" },
                { id: "truck", label: "Truck", item: "Truck" },
              ],
            }
          );

          console.log(
            "Popup result - confirmed:",
            confirmed,
            "payload:",
            payload
          );

          if (!confirmed) {
            console.log("User cancelled vehicle selection");
            return; // Batalkan pembayaran jika tidak memilih
          }

          // Set vehicle type langsung ke property order
          const vehicleType = payload;
          console.log("Setting vehicle type to:", vehicleType);
          console.log("Payload received:", payload);

          order.pertamina_vehicle_type = vehicleType;

          console.log("Vehicle type set to:", vehicleType);
          console.log(
            "Order vehicle type after set:",
            order.pertamina_vehicle_type
          );
          console.log("Order object:", order);

          // Coba force trigger save
          if (order.save_to_db) {
            order.save_to_db();
          }
        }

        return super._onClickPay();
      }
    };

  Registries.Component.extend(ProductScreen, CustomProductScreen);

  // Extend Order model
  const PosOrderWithVehicle = (Order) =>
    class extends Order {
      constructor() {
        super(...arguments);
        this.pertamina_vehicle_type = this.pertamina_vehicle_type || null;
      }

      export_as_JSON() {
        const json = super.export_as_JSON();
        json.pertamina_vehicle_type = this.pertamina_vehicle_type || null;
        console.log(
          "Exporting JSON with vehicle type:",
          json.pertamina_vehicle_type
        );
        return json;
      }

      init_from_JSON(json) {
        super.init_from_JSON(json);
        this.pertamina_vehicle_type = json.pertamina_vehicle_type || null;
        console.log(
          "Initializing from JSON with vehicle type:",
          this.pertamina_vehicle_type
        );
      }

      // PENTING: Method ini yang mengirim data ke template receipt
      export_for_printing() {
        const receipt = super.export_for_printing();
        receipt.pertamina_vehicle_type = this.pertamina_vehicle_type || null;
        console.log(
          "Receipt data with vehicle:",
          receipt.pertamina_vehicle_type
        ); // Debug log
        return receipt;
      }
    };

  Registries.Model.extend(Order, PosOrderWithVehicle);

  return {
    PosOrderWithVehicle,
    CustomProductScreen,
  };
});
