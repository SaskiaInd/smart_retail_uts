import sqlite3
import os
from datetime import datetime

DB_NAME = "smart_retail.db"


def koneksi():
    return sqlite3.connect(DB_NAME)


def buat_tabel():
    conn = koneksi()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS produk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_produk TEXT,
        harga_modal INTEGER,
        harga_jual INTEGER,
        stok INTEGER)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS transaksi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT,
        total_bayar INTEGER)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS detail_transaksi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_transaksi INTEGER,
        id_produk INTEGER,
        jumlah INTEGER,
        subtotal INTEGER)""")

    conn.commit()
    conn.close()


def isi_data_awal():
    conn = koneksi()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                    ("admin", "admin123", "admin"))
        cur.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                    ("kasir", "kasir123", "kasir"))

    cur.execute("SELECT COUNT(*) FROM produk")
    if cur.fetchone()[0] == 0:
        data = [("Beras 5 Kg", 70000, 75000, 20),
                ("Gula 1 Kg", 15000, 18000, 30),
                ("Minyak Goreng", 19000, 22000, 25),
                ("Mie Instan", 3000, 3500, 100)]
        cur.executemany("INSERT INTO produk (nama_produk, harga_modal, harga_jual, stok) VALUES (?,?,?,?)", data)

    conn.commit()
    conn.close()


def login():
    while True:
        username = input("Username: ")
        password = input("Password: ")

        conn = koneksi()
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE username=? AND password=?",
                    (username, password))
        hasil = cur.fetchone()
        conn.close()

        if hasil is None:
            print("Username atau password salah!\n")
        else:
            print(f"Login berhasil sebagai {hasil[0]}\n")
            return hasil[0]


def format_rupiah(angka):
    return "Rp" + f"{angka:,}".replace(",", ".")


# ===================== PRODUK =====================

def lihat_produk():
    conn = koneksi()
    cur = conn.cursor()
    cur.execute("SELECT id, nama_produk, harga_modal, harga_jual, stok FROM produk")
    produk_data = cur.fetchall()
    conn.close()

    if not produk_data:
        print("Belum ada produk.\n")
        return

    print("\n===== DAFTAR PRODUK =====")
    print(f"{'ID':<5}{'Nama Produk':<20}{'Harga Modal':<15}{'Harga Jual':<15}{'Stok':<10}")
    print("-" * 65)
    for produk in produk_data:
        print(f"{produk[0]:<5}{produk[1]:<20}{produk[2]:<15}{produk[3]:<15}{produk[4]:<10}")
    print("-" * 65)


def lihat_produk_kasir():
    """Tampilan daftar produk untuk kasir, tanpa menampilkan harga modal."""
    conn = koneksi()
    cur = conn.cursor()
    cur.execute("SELECT id, nama_produk, harga_jual, stok FROM produk")
    produk_data = cur.fetchall()
    conn.close()

    if not produk_data:
        print("Belum ada produk.\n")
        return

    print("\n===== DAFTAR PRODUK =====")
    print(f"{'ID':<5}{'Nama Produk':<20}{'Harga Jual':<15}{'Stok':<10}")
    print("-" * 50)
    for produk in produk_data:
        print(f"{produk[0]:<5}{produk[1]:<20}{produk[2]:<15}{produk[3]:<10}")
    print("-" * 50)


def tambah_produk():
    print("\n===== TAMBAH PRODUK =====")
    nama_produk = input("Nama Produk: ")
    try:
        harga_modal = int(input("Harga Modal: "))
        harga_jual = int(input("Harga Jual: "))
        stok = int(input("Stok: "))
    except ValueError:
        print("Harga modal, harga jual, dan stok harus berupa angka.\n")
        return

    conn = koneksi()
    cur = conn.cursor()
    cur.execute("INSERT INTO produk (nama_produk, harga_modal, harga_jual, stok) VALUES (?,?,?,?)",
                (nama_produk, harga_modal, harga_jual, stok))
    conn.commit()
    conn.close()
    print(f"Produk '{nama_produk}' berhasil ditambahkan.\n")


def edit_produk():
    print("\n===== EDIT PRODUK =====")
    lihat_produk()
    try:
        id_produk = int(input("Masukkan ID produk yang ingin diedit: "))
    except ValueError:
        print("ID produk harus berupa angka.\n")
        return

    conn = koneksi()
    cur = conn.cursor()
    cur.execute("SELECT nama_produk, harga_modal, harga_jual, stok FROM produk WHERE id=?", (id_produk,))
    produk = cur.fetchone()

    if produk is None:
        print("Produk tidak ditemukan.\n")
        conn.close()
        return

    print(f"Data Produk Saat Ini: {produk[0]}, Harga Modal: {produk[1]}, Harga Jual: {produk[2]}, Stok: {produk[3]}")
    nama_produk_baru = input(f"Nama Produk Baru (kosongkan jika tidak ingin mengubah, saat ini: {produk[0]}): ")
    harga_modal_baru = input(f"Harga Modal Baru (kosongkan jika tidak ingin mengubah, saat ini: {produk[1]}): ")
    harga_jual_baru = input(f"Harga Jual Baru (kosongkan jika tidak ingin mengubah, saat ini: {produk[2]}): ")
    stok_baru = input(f"Stok Baru (kosongkan jika tidak ingin mengubah, saat ini: {produk[3]}): ")

    updates = []
    params = []

    if nama_produk_baru:
        updates.append("nama_produk=?")
        params.append(nama_produk_baru)
    if harga_modal_baru:
        try:
            updates.append("harga_modal=?")
            params.append(int(harga_modal_baru))
        except ValueError:
            print("Harga modal harus berupa angka. Perubahan ini diabaikan.\n")
    if harga_jual_baru:
        try:
            updates.append("harga_jual=?")
            params.append(int(harga_jual_baru))
        except ValueError:
            print("Harga jual harus berupa angka. Perubahan ini diabaikan.\n")
    if stok_baru:
        try:
            updates.append("stok=?")
            params.append(int(stok_baru))
        except ValueError:
            print("Stok harus berupa angka. Perubahan ini diabaikan.\n")

    if updates:
        query = f"UPDATE produk SET {', '.join(updates)} WHERE id=?"
        params.append(id_produk)
        cur.execute(query, tuple(params))
        conn.commit()
        print("Produk berhasil diperbarui.\n")
    else:
        print("Tidak ada perubahan dilakukan.\n")

    conn.close()


def hapus_produk():
    print("\n===== HAPUS PRODUK =====")
    lihat_produk()
    try:
        id_produk = int(input("Masukkan ID produk yang ingin dihapus: "))
    except ValueError:
        print("ID produk harus berupa angka.\n")
        return

    conn = koneksi()
    cur = conn.cursor()
    cur.execute("DELETE FROM produk WHERE id=?", (id_produk,))
    conn.commit()
    if cur.rowcount > 0:
        print("Produk berhasil dihapus.\n")
    else:
        print("Produk tidak ditemukan.\n")
    conn.close()


def kelola_produk():
    """Menu ini HANYA dipanggil dari menu_admin(). Kasir tidak pernah punya akses ke sini."""
    while True:
        print("\n===== KELOLA PRODUK (ADMIN) =====")
        print("1. Tambah Produk")
        print("2. Edit Produk")
        print("3. Hapus Produk")
        print("4. Lihat Produk")
        print("5. Kembali ke Menu Utama")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_produk()
        elif pilihan == "2":
            edit_produk()
        elif pilihan == "3":
            hapus_produk()
        elif pilihan == "4":
            lihat_produk()
        elif pilihan == "5":
            break
        else:
            print("Pilihan tidak valid!")


def cari_produk():
    kata = input("Cari Produk : ")

    conn = koneksi()
    cur = conn.cursor()

    if kata.isdigit():
        cur.execute("SELECT id, nama_produk, harga_jual, stok FROM produk WHERE id=?",
                    (int(kata),))
    else:
        cur.execute("SELECT id, nama_produk, harga_jual, stok FROM produk WHERE nama_produk LIKE ?",
                    ("%" + kata + "%",))

    hasil = cur.fetchall()
    conn.close()

    if len(hasil) == 0:
        print("Produk tidak ditemukan.")
    else:
        print(f"{'ID':<5}{'Nama Barang':<20}{'Harga Jual':<12}{'Stok':<6}")
        print("-" * 43)
        for baris in hasil:
            print(f"{baris[0]:<5}{baris[1]:<20}{baris[2]:<12}{baris[3]:<6}")


# ===================== CETAK STRUK =====================

def cetak_struk_txt(nama_file, id_transaksi, tanggal, keranjang, total, bayar, kembalian):
    with open(nama_file, "w", encoding="utf-8") as f:
        f.write("==========================\n")
        f.write("        SMART RETAIL\n")
        f.write("==========================\n")
        f.write(f"No. Transaksi : {id_transaksi}\n")
        f.write(f"Tanggal       : {tanggal}\n")
        f.write("--------------------------\n")
        for item in keranjang:
            f.write(f"{item['nama']:<16}{item['jumlah']} x {format_rupiah(item['harga'])}\n")
            f.write(f"{'':<16}Subtotal: {format_rupiah(item['subtotal'])}\n")
        f.write("--------------------------\n")
        f.write(f"TOTAL      : {format_rupiah(total)}\n")
        f.write(f"BAYAR      : {format_rupiah(bayar)}\n")
        f.write(f"KEMBALIAN  : {format_rupiah(kembalian)}\n")
        f.write("==========================\n")
        f.write("     Terima kasih telah\n")
        f.write("        berbelanja!\n")
        f.write("==========================\n")
    print(f"Struk berhasil disimpan sebagai '{nama_file}'\n")


def cetak_struk_pdf(nama_file, id_transaksi, tanggal, keranjang, total, bayar, kembalian):
    try:
        from reportlab.lib.pagesizes import A6
        from reportlab.pdfgen import canvas
    except ImportError:
        print("Library 'reportlab' belum terpasang.")
        print("Silakan install terlebih dahulu dengan perintah:")
        print("    pip install reportlab")
        print("Struk tidak jadi dicetak dalam format PDF.\n")
        return

    lebar, tinggi = A6
    c = canvas.Canvas(nama_file, pagesize=A6)
    y = tinggi - 30

    def tulis(teks, ukuran=10, tebal=False, tengah=False):
        nonlocal y
        font = "Helvetica-Bold" if tebal else "Helvetica"
        c.setFont(font, ukuran)
        if tengah:
            c.drawCentredString(lebar / 2, y, teks)
        else:
            c.drawString(20, y, teks)
        y -= ukuran + 4

    tulis("SMART RETAIL", 14, tebal=True, tengah=True)
    tulis(f"No. Transaksi : {id_transaksi}")
    tulis(f"Tanggal       : {tanggal}")
    tulis("-" * 34)

    for item in keranjang:
        tulis(f"{item['nama']} x{item['jumlah']}")
        tulis(f"   @ {format_rupiah(item['harga'])} = {format_rupiah(item['subtotal'])}")

    tulis("-" * 34)
    tulis(f"TOTAL     : {format_rupiah(total)}", tebal=True)
    tulis(f"BAYAR     : {format_rupiah(bayar)}")
    tulis(f"KEMBALIAN : {format_rupiah(kembalian)}")
    tulis("-" * 34)
    tulis("Terima kasih telah berbelanja!", tengah=True)

    c.save()
    print(f"Struk berhasil disimpan sebagai '{nama_file}'\n")


def tawarkan_cetak_struk(id_transaksi, tanggal, keranjang, total, bayar, kembalian):
    print("\nCetak struk?")
    print("1. Simpan sebagai TXT")
    print("2. Simpan sebagai PDF")
    print("3. Tidak usah")
    pilihan = input("Pilih: ")

    folder_struk = "struk"
    os.makedirs(folder_struk, exist_ok=True)

    if pilihan == "1":
        nama_file = os.path.join(folder_struk, f"struk_{id_transaksi}.txt")
        cetak_struk_txt(nama_file, id_transaksi, tanggal, keranjang, total, bayar, kembalian)
    elif pilihan == "2":
        nama_file = os.path.join(folder_struk, f"struk_{id_transaksi}.pdf")
        cetak_struk_pdf(nama_file, id_transaksi, tanggal, keranjang, total, bayar, kembalian)
    else:
        print("Struk tidak dicetak.\n")


# ===================== TRANSAKSI =====================

def transaksi_penjualan():
    keranjang = []

    while True:
        lihat_produk_kasir()
        id_produk = input("\nID Barang (kosongkan untuk selesai): ")
        if id_produk == "":
            break
        if not id_produk.isdigit():
            print("ID produk harus berupa angka.\n")
            continue
        id_produk = int(id_produk)

        conn = koneksi()
        cur = conn.cursor()
        cur.execute("SELECT id, nama_produk, harga_jual, stok FROM produk WHERE id=?",
                    (id_produk,))
        produk = cur.fetchone()
        conn.close()

        if produk is None:
            print("Produk tidak ditemukan!")
            continue

        sudah_di_keranjang = 0
        for item in keranjang:
            if item["id"] == produk[0]:
                sudah_di_keranjang += item["jumlah"]
        sisa_stok = produk[3] - sudah_di_keranjang

        while True:
            try:
                jumlah = int(input(f"Jumlah Pembelian (stok tersedia: {sisa_stok}): "))
            except ValueError:
                print("Jumlah harus berupa angka.")
                continue
            if jumlah <= 0:
                print("Jumlah harus lebih dari 0.")
            elif jumlah > sisa_stok:
                print("ERROR:")
                print("Stok tidak mencukupi.")
                print("Silakan masukkan jumlah yang lebih kecil.")
            else:
                break

        subtotal = produk[2] * jumlah

        keranjang.append({
            "id": produk[0],
            "nama": produk[1],
            "harga": produk[2],
            "jumlah": jumlah,
            "subtotal": subtotal
        })
        print(f"{produk[1]} x{jumlah} ditambahkan ke keranjang.")

        lagi = input("Tambah barang lain? (Y/T): ").upper()
        if lagi != "Y":
            break

    if len(keranjang) == 0:
        print("Tidak ada barang di keranjang. Transaksi dibatalkan.")
        return

    total = sum(item["subtotal"] for item in keranjang)

    print(f"\nTotal Belanja : {format_rupiah(total)}")
    while True:
        try:
            bayar = int(input("Uang Bayar    : "))
            if bayar < total:
                print("Uang bayar kurang dari total belanja.")
                continue
            break
        except ValueError:
            print("Uang bayar harus berupa angka.")
    kembalian = bayar - total

    print("\n==========================")
    print("SMART RETAIL")
    print("==========================")
    for item in keranjang:
        print(f"{item['nama']:<16}{item['jumlah']} x {item['harga']}")
    print("--------------------------")
    print(f"TOTAL = {format_rupiah(total)}")
    print(f"Kembalian : {format_rupiah(kembalian)}")
    print("==========================")

    tanggal = datetime.now().strftime("%d/%m/%Y %H:%M")

    conn = koneksi()
    cur = conn.cursor()
    cur.execute("INSERT INTO transaksi (tanggal, total_bayar) VALUES (?,?)",
                (tanggal, total))
    id_transaksi = cur.lastrowid

    for item in keranjang:
        cur.execute("INSERT INTO detail_transaksi (id_transaksi, id_produk, jumlah, subtotal) VALUES (?,?,?,?)",
                    (id_transaksi, item["id"], item["jumlah"], item["subtotal"]))
        cur.execute("UPDATE produk SET stok = stok - ? WHERE id = ?",
                    (item["jumlah"], item["id"]))
    conn.commit()
    conn.close()

    tawarkan_cetak_struk(id_transaksi, tanggal, keranjang, total, bayar, kembalian)


def riwayat_transaksi():
    """Menu ini HANYA dipanggil dari menu_admin(). Kasir tidak pernah punya akses ke sini."""
    conn = koneksi()
    cur = conn.cursor()
    cur.execute("SELECT id, tanggal, total_bayar FROM transaksi ORDER BY id")
    semua = cur.fetchall()
    conn.close()

    if len(semua) == 0:
        print("Belum ada transaksi.")
        return

    print(f"\n{'ID':<5}{'Tanggal':<18}{'Total':<12}")
    print("-" * 35)
    for baris in semua:
        print(f"{baris[0]:<5}{baris[1]:<18}{format_rupiah(baris[2]):<12}")


def laporan_penjualan():
    """Menu ini HANYA dipanggil dari menu_admin(). Kasir tidak pernah punya akses ke sini."""
    conn = koneksi()
    cur = conn.cursor()

    print("\n===== LAPORAN PENJUALAN =====")

    cur.execute("SELECT COUNT(*), SUM(total_bayar) FROM transaksi")
    jumlah_trx, pendapatan = cur.fetchone()
    if pendapatan is None:
        pendapatan = 0

    print(f"Jumlah Transaksi : {jumlah_trx}")
    print(f"Total Penjualan  : {format_rupiah(pendapatan)}")

    cur.execute("""SELECT p.nama_produk, SUM(d.jumlah) AS total_terjual
                   FROM detail_transaksi d
                   JOIN produk p ON d.id_produk = p.id
                   GROUP BY d.id_produk
                   ORDER BY total_terjual DESC
                   LIMIT 1""")
    terlaris = cur.fetchone()

    print("\nProduk Terlaris :")
    if terlaris is None:
        print("Belum ada penjualan.")
    else:
        print(f"{terlaris[0]}")
        print(f"Terjual {terlaris[1]} pcs")

    cur.execute("SELECT nama_produk, stok FROM produk WHERE stok < 10")
    stok_menipis = cur.fetchall()

    print("\nProduk yang harus segera restock:")
    if len(stok_menipis) == 0:
        print("Tidak ada produk dengan stok menipis.")
    else:
        for nama, stok in stok_menipis:
            print(f"- {nama} (sisa {stok} pcs)")

    conn.close()


# ===================== MENU PER ROLE =====================

def menu_admin():
    """Admin: kelola produk (tambah/edit/hapus/lihat), lihat riwayat transaksi, lihat laporan penjualan."""
    while True:
        print("\n===== MENU ADMIN =====")
        print("1. Kelola Produk")
        print("2. Cari Produk")
        print("3. Riwayat Transaksi")
        print("4. Laporan Penjualan")
        print("5. Logout")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            kelola_produk()
        elif pilihan == "2":
            cari_produk()
        elif pilihan == "3":
            riwayat_transaksi()
        elif pilihan == "4":
            laporan_penjualan()
        elif pilihan == "5":
            print("Logout berhasil.")
            break
        else:
            print("Pilihan tidak valid!")


def menu_kasir():
    """Kasir: HANYA transaksi penjualan dan melihat daftar produk.
    Tidak ada opsi Tambah/Edit/Hapus Produk maupun Riwayat Transaksi di menu ini."""
    while True:
        print("\n===== MENU KASIR =====")
        print("1. Transaksi Penjualan")
        print("2. Lihat Daftar Produk")
        print("3. Logout")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            transaksi_penjualan()
        elif pilihan == "2":
            lihat_produk_kasir()
        elif pilihan == "3":
            print("Logout berhasil.")
            break
        else:
            print("Pilihan tidak valid!")


def menu_utama(role):
    if role == "admin":
        menu_admin()
    elif role == "kasir":
        menu_kasir()
    else:
        print("Role tidak dikenali. Program dihentikan.")


# ===== Program utama =====
if __name__ == "__main__":
    buat_tabel()
    isi_data_awal()
    role = login()
    menu_utama(role)
