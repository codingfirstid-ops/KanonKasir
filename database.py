import sqlite3


DATABASE = 'kasir.db'   # nama file database kita


def get_db():
    """Buka koneksi ke database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # supaya hasil bisa diakses seperti dict
    return conn


def init_db():
    """Buat tabel-tabel yang dibutuhkan (jalankan sekali di awal)"""
    conn = get_db()
    cursor = conn.cursor()


    # Tabel produk: menyimpan daftar barang yang dijual
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produk (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nama    TEXT    NOT NULL,
            harga   INTEGER NOT NULL,
            stok    INTEGER DEFAULT 0
        )
    ''')


    # Tabel transaksi: menyimpan setiap penjualan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaksi (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal     TEXT    DEFAULT CURRENT_TIMESTAMP,
            nama_pembeli TEXT   NOT NULL,
            total       INTEGER NOT NULL,
            bayar       INTEGER NOT NULL,
            kembalian   INTEGER NOT NULL
        )
    ''')


    # Tabel detail_transaksi: barang apa saja yang dibeli per transaksi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detail_transaksi (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            transaksi_id   INTEGER NOT NULL,
            produk_id      INTEGER NOT NULL,
            nama_produk    TEXT    NOT NULL,
            harga          INTEGER NOT NULL,
            jumlah         INTEGER NOT NULL,
            subtotal       INTEGER NOT NULL,
            FOREIGN KEY (transaksi_id) REFERENCES transaksi(id)
        )
    ''')


    conn.commit()   # simpan perubahan
    conn.close()    # tutup koneksi
    print('Database siap!')

# ─── FUNGSI PRODUK ───────────────────────────────


def tambah_produk(nama, harga, stok):
    """Simpan produk baru ke database"""
    conn = get_db()
    conn.execute(
        'INSERT INTO produk (nama, harga, stok) VALUES (?, ?, ?)',
        (nama, harga, stok)
    )
    conn.commit()
    conn.close()


def get_semua_produk():
    """Ambil semua produk dari database"""
    conn = get_db()
    produk = conn.execute('SELECT * FROM produk ORDER BY nama').fetchall()
    conn.close()
    return produk


def get_produk_by_id(produk_id):
    """Ambil satu produk berdasarkan ID"""
    conn = get_db()
    produk = conn.execute(
        'SELECT * FROM produk WHERE id = ?', (produk_id,)
    ).fetchone()
    conn.close()
    return produk




# ─── FUNGSI TRANSAKSI ───────────────────────────


def simpan_transaksi(nama_pembeli, total, bayar, kembalian, keranjang):
    """Simpan transaksi + detail ke database"""
    conn = get_db()
    cursor = conn.cursor()


    # Simpan transaksi utama
    cursor.execute(
        '''INSERT INTO transaksi (nama_pembeli, total, bayar, kembalian)
           VALUES (?, ?, ?, ?)''',
        (nama_pembeli, total, bayar, kembalian)
    )
    transaksi_id = cursor.lastrowid  # ambil ID transaksi yang baru disimpan


    # Simpan detail setiap barang
    for item in keranjang:
        cursor.execute(
            '''INSERT INTO detail_transaksi
               (transaksi_id, produk_id, nama_produk, harga, jumlah, subtotal)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (transaksi_id, item['produk_id'], item['nama'],
             item['harga'], item['jumlah'], item['subtotal'])
        )


    conn.commit()
    conn.close()
    return transaksi_id


def get_semua_transaksi():
    """Ambil semua transaksi (untuk riwayat)"""
    conn = get_db()
    data = conn.execute(
        'SELECT * FROM transaksi ORDER BY tanggal DESC'
    ).fetchall()
    conn.close()
    return data


def get_total_penjualan_hari_ini():
    """Hitung total penjualan hari ini (untuk dashboard)"""
    conn = get_db()
    result = conn.execute(
        '''SELECT COUNT(*) as jumlah_transaksi, SUM(total) as total_penjualan
           FROM transaksi
           WHERE DATE(tanggal) = DATE('now', 'localtime')'''
    ).fetchone()
    conn.close()
    return result

# Tambahkan di database.py


def get_dashboard_data():
    """Ambil semua data yang dibutuhkan dashboard"""
    conn = get_db()


    # Total transaksi & penjualan hari ini
    hari_ini = conn.execute('''
        SELECT
            COUNT(*)    AS jumlah_transaksi,
            COALESCE(SUM(total), 0) AS total_penjualan
        FROM transaksi
        WHERE DATE(tanggal) = DATE('now', 'localtime')
    ''').fetchone()


    # 5 transaksi terakhir
    riwayat = conn.execute('''
        SELECT id, tanggal, nama_pembeli, total
        FROM transaksi
        ORDER BY tanggal DESC
        LIMIT 5
    ''').fetchall()


    # Produk terlaris (berdasarkan jumlah terjual)
    terlaris = conn.execute('''
        SELECT nama_produk,
               SUM(jumlah)   AS total_terjual,
               SUM(subtotal) AS total_pendapatan
        FROM detail_transaksi
        GROUP BY nama_produk
        ORDER BY total_terjual DESC
        LIMIT 5
    ''').fetchall()


    # Total semua transaksi (keseluruhan)
    semua = conn.execute('''
        SELECT COUNT(*) AS total_tx, COALESCE(SUM(total),0) AS total_omzet
        FROM transaksi
    ''').fetchone()


    conn.close()
    return {
        'hari_ini':  hari_ini,
        'riwayat':   riwayat,
        'terlaris':  terlaris,
        'semua':     semua
    }


