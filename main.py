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

# ===== Program utama =====
buat_tabel()
isi_data_awal()
print("Database siap!")
