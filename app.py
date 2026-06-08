from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, tambah_produk, get_semua_produk


app = Flask(__name__)
app.secret_key = 'kasir-rahasia-123'

# Inisialisasi database saat pertama kali app jalan
with app.app_context():
    init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/produk')
def produk():
    daftar = get_semua_produk()
    return render_template('produk.html', produk_list=daftar)


@app.route('/produk/tambah', methods=['GET', 'POST'])
def tambah_produk_view():
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        try:
            harga = int(request.form.get('harga', 0))
        except ValueError:
            harga = 0
        try:
            stok = int(request.form.get('stok', 0))
        except ValueError:
            stok = 0

        if not nama or harga <= 0:
            flash('Nama dan harga tidak boleh kosong!', 'error')
        else:
            tambah_produk(nama, harga, stok)
            flash(f'Produk {nama} berhasil ditambahkan!', 'success')
            return redirect(url_for('produk'))

    return render_template('tambah_produk.html')


if __name__ == '__main__':
    app.run(debug=True)
