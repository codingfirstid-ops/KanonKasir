from flask import Flask, render_template
app = Flask(__name__)
@app.route('/')
def halaman_utama():
    nama_warung = "Warung Serba Ada"

    return render_template('index.html',warung=nama_warung)
@app.route('/produk')    
def halaman_produk():
    return render_template('produk.html')
if __name__ == '__main__':
    app.run(debug=True)