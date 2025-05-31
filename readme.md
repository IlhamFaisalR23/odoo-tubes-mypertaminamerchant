# 🛒 Odoo 16 - POS Pertamina

`pos_pertamina` adalah modul utama untuk mengelola berbagai fitur kustom terkait Point of Sale (POS) di lingkungan Pertamina, dikembangkan untuk Odoo 16.

Modul ini dirancang secara modular, dengan submodule terpisah di dalamnya untuk setiap fitur. Hal ini memudahkan manajemen, pengembangan, dan pemeliharaan fitur secara terpisah namun tetap dalam satu ekosistem modul utama.

---

## 📁 Struktur Folder

pos_pertamina/
├── init.py
├── manifest.py
├── pertamina_product_seed/
├── upgrade_pemantauan_stok/ <-- SuB Module>


- `pertamina_product_seed/`: Submodule untuk men-setup data awal produk Pertamina.
- `upgrade_pemantauan_stok/`: Submodule untuk peningkatan fitur pemantauan stok.

Setiap submodule mengikuti struktur standar modul Odoo (dengan `__init__.py`, `__manifest__.py`, dsb).

---

## 🛠️ Cara Instalasi

Ikuti langkah-langkah berikut untuk menginstal modul ini pada Odoo 16:

### 1. **Copy Folder ke Addons**

Salin seluruh folder `pos_pertamina` ke direktori addons Odoo. Contoh lokasi default untuk Odoo Windows:

C:\Program Files\Odoo 16.0.20250210\server\odoo\addons


### 2. **Restart Odoo Server**

Buka Command Prompt sebagai Administrator, lalu jalankan:

```bash
net stop odoo-server-16.0
net start odoo-server-16.0

3. Aktifkan Developer Mode
Login ke Odoo sebagai Administrator.

Aktifkan Developer Mode melalui menu:

Klik user di pojok kanan atas → "Aktifkan Mode Developer"

Atau tambahkan ?debug=1 pada URL Odoo Anda

4. Update Apps List
Masuk ke menu Apps

Klik tombol Update Apps List

Cari POS Pertamina lalu klik Install
