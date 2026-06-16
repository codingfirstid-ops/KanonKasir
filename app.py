from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, tambah_produk, get_semua_produk
from flask import session
from database import simpan_transaksi, get_semua_produk, get_produk_by_id
import json


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

@app.route('/kasir')
def kasir():
    produk_list = get_semua_produk()
    keranjang   = session.get('keranjang', [])
    total = sum(item['subtotal'] for item in keranjang)
    return render_template('kasir.html',
        produk_list=produk_list,
        keranjang=keranjang,
        total=total)


@app.route('/kasir/tambah', methods=['POST'])
def tambah_ke_keranjang():
    produk_id = int(request.form['produk_id'])
    jumlah    = int(request.form['jumlah'])
    produk    = get_produk_by_id(produk_id)


    keranjang = session.get('keranjang', [])


    # Cek apakah produk sudah ada di keranjang
    sudah_ada = False
    for item in keranjang:
        if item['produk_id'] == produk_id:
            item['jumlah']   += jumlah
            item['subtotal']  = item['harga'] * item['jumlah']
            sudah_ada = True
            break


    if not sudah_ada:
        keranjang.append({
            'produk_id': produk_id,
            'nama':      produk['nama'],
            'harga':     produk['harga'],
            'jumlah':    jumlah,
            'subtotal':  produk['harga'] * jumlah
        })


    session['keranjang'] = keranjang
    session.modified = True
    return redirect(url_for('kasir'))


@app.route('/kasir/hapus/<int:produk_id>')
def hapus_dari_keranjang(produk_id):
    keranjang = session.get('keranjang', [])
    session['keranjang'] = [i for i in keranjang if i['produk_id'] != produk_id]
    session.modified = True
    return redirect(url_for('kasir'))


@app.route('/kasir/bayar', methods=['POST'])
def bayar():
    keranjang    = session.get('keranjang', [])
    nama_pembeli = request.form['nama_pembeli']
    bayar_input  = int(request.form['bayar'])
    total        = sum(item['subtotal'] for item in keranjang)


    if bayar_input < total:
        flash('Uang tidak cukup!', 'error')
        return redirect(url_for('kasir'))


    kembalian    = bayar_input - total
    transaksi_id = simpan_transaksi(
        nama_pembeli, total, bayar_input, kembalian, keranjang
    )


    session.pop('keranjang', None)  # kosongkan keranjang setelah bayar


    return render_template('struk.html',
        nama_pembeli=nama_pembeli,
        keranjang=keranjang,
        total=total,
        bayar=bayar_input,
        kembalian=kembalian,
        transaksi_id=transaksi_id)

# Tambahkan di app.py
from database import get_dashboard_data


@app.route('/dashboard')
def dashboard():
    data = get_dashboard_data()
    return render_template('dashboard.html', data=data)

# app.py — VERSI FINAL
from flask import (Flask, render_template, request,
                   redirect, url_for, flash, session)
from database import (init_db, tambah_produk, get_semua_produk,
                      get_produk_by_id, simpan_transaksi,
                      get_semua_transaksi, get_dashboard_data)


app = Flask(__name__)
app.secret_key = 'kasir-super-rahasia-2024'


# Inisialisasi database saat pertama kali app jalan
with app.app_context():
    init_db()


# ── HALAMAN UTAMA ──────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('kasir'))


# ── KASIR ──────────────────────────────────────
@app.route('/kasir')
def kasir():
    produk_list = get_semua_produk()
    keranjang   = session.get('keranjang', [])
    total = sum(i['subtotal'] for i in keranjang)
    return render_template('kasir.html',
        produk_list=produk_list, keranjang=keranjang, total=total)


@app.route('/kasir/tambah', methods=['POST'])
def tambah_ke_keranjang():
    pid    = int(request.form['produk_id'])
    jumlah = int(request.form['jumlah'])
    produk = get_produk_by_id(pid)
    keranjang = session.get('keranjang', [])
    sudah_ada = False
    for item in keranjang:
        if item['produk_id'] == pid:
            item['jumlah'] += jumlah
            item['subtotal'] = item['harga'] * item['jumlah']
            sudah_ada = True; break
    if not sudah_ada:
        keranjang.append({'produk_id':pid,'nama':produk['nama'],
            'harga':produk['harga'],'jumlah':jumlah,
            'subtotal':produk['harga']*jumlah})
    session['keranjang'] = keranjang
    session.modified = True
    return redirect(url_for('kasir'))


@app.route('/kasir/hapus/<int:pid>')
def hapus_dari_keranjang(pid):
    keranjang = [i for i in session.get('keranjang',[]) if i['produk_id']!=pid]
    session['keranjang'] = keranjang
    session.modified = True
    return redirect(url_for('kasir'))


@app.route('/kasir/kosongkan')
def kosongkan_keranjang():
    session.pop('keranjang', None)
    return redirect(url_for('kasir'))


@app.route('/kasir/bayar', methods=['POST'])
def bayar():
    keranjang    = session.get('keranjang', [])
    nama_pembeli = request.form['nama_pembeli']
    bayar_input  = int(request.form['bayar'])
    total        = sum(i['subtotal'] for i in keranjang)
    if not keranjang:
        flash('Keranjang kosong!', 'error')
        return redirect(url_for('kasir'))
    if bayar_input < total:
        flash('Uang tidak cukup!', 'error')
        return redirect(url_for('kasir'))
    kembalian = bayar_input - total
    tid = simpan_transaksi(nama_pembeli, total, bayar_input, kembalian, keranjang)
    session.pop('keranjang', None)
    return render_template('struk.html', nama_pembeli=nama_pembeli,
        keranjang=keranjang, total=total, bayar=bayar_input,
        kembalian=kembalian, transaksi_id=tid)


# ── PRODUK ─────────────────────────────────────
@app.route('/produk')
def produk():
    return render_template('produk.html', produk_list=get_semua_produk())


@app.route('/produk/tambah', methods=['GET','POST'])
def tambah_produk_view():
    if request.method == 'POST':
        nama  = request.form['nama'].strip()
        harga = int(request.form['harga'])
        stok  = int(request.form.get('stok', 0))
        if not nama or harga <= 0:
            flash('Data tidak valid!', 'error')
        else:
            tambah_produk(nama, harga, stok)
            flash(f'Produk {nama} berhasil ditambahkan!', 'success')
            return redirect(url_for('produk'))
    return render_template('tambah_produk.html')


# ── DASHBOARD ──────────────────────────────────
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', data=get_dashboard_data())


if __name__ == '__main__':
    app.run(debug=True)


