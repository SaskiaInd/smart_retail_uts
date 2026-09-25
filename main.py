import sqlite3

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
    while True:
        print("\n===== KELOLA PRODUK =====")
        print("1. Tambah Produk")
        print("2. Edit Produk")
        print("3. Hapus Produk")
        print("4. Lihat Produk")
        print("5. Lihat Riwayat Transaksi")
        print("6. Kembali ke Menu Utama")
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
            riwayat_transaksi()
        elif pilihan == "6":
            break
        else:
            print("Pilihan tidak valid!")


def format_rupiah(angka):
    return "Rp" + f"{angka:,}".replace(",", ".")

def transaksi_penjualan():
    keranjang = []

    while True:
        lihat_produk()
        id_produk = input("\nID Barang (kosongkan untuk selesai): ")
        if id_produk == "":
            break
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

        # cek berapa jumlah barang ini yang sudah ada di keranjang
        sudah_di_keranjang = 0
        for item in keranjang:
            if item["id"] == produk[0]:
                sudah_di_keranjang += item["jumlah"]
        sisa_stok = produk[3] - sudah_di_keranjang

        while True:
            jumlah = int(input(f"Jumlah Pembelian (stok tersedia: {sisa_stok}): "))
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

    total = 0
    for item in keranjang:
        total += item["subtotal"]

    print(f"\nTotal Belanja : {format_rupiah(total)}")
    bayar = int(input("Uang Bayar    : "))
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
    # simpan transaksi ke database dan kurangi stok
    from datetime import datetime
    tanggal = datetime.now().strftime("%d/%m/%Y")

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

def riwayat_transaksi():
    conn = koneksi()
    cur = conn.cursor()
    cur.execute("SELECT id, tanggal, total_bayar FROM transaksi ORDER BY id")
    semua = cur.fetchall()
    conn.close()

    if len(semua) == 0:
        print("Belum ada transaksi.")
        return

    print(f"\n{'ID':<5}{'Tanggal':<14}{'Total':<12}")
    print("-" * 31)
    for baris in semua:
        print(f"{baris[0]:<5}{baris[1]:<14}{format_rupiah(baris[2]):<12}")

def menu_utama(role):
    while True:
        print("\n===== SMART RETAIL =====")
        print("1. Kelola Produk")
        print("2. Transaksi Penjualan")
        print("3. Cari Produk")
        print("4. Laporan Penjualan")
        print("5. Logout")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            kelola_produk()
        elif pilihan == "2":
            if role == "kasir":
                transaksi_penjualan()
            else:
                print("Menu ini hanya untuk kasir.")
        elif pilihan == "3":
            print("(Cari Produk belum dibuat)")
        elif pilihan == "4":
            print("(Laporan belum dibuat)")
        elif pilihan == "5":
            print("Logout berhasil.")
            break
        else:
            print("Pilihan tidak valid!")

# ===== Program utama =====
buat_tabel()
isi_data_awal()
role = login()
menu_utama(role)
