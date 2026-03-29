
# SMARTCASHIER WEB

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'secret123'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL", 
    "sqlite:///smartcashier.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
PPN = 0.11

# VALIDASI 
def validasi_email(email):
    if email.count("@") != 1:
        return False
    username, domain = email.split("@")
    if "." not in domain:
        return False
    return True

#  MODELS 
class User(db.Model):
    userid = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(100))
    nama = db.Column(db.String(100))
    email = db.Column(db.String(100))
    usia = db.Column(db.Integer)

class Barang(db.Model):
    kode = db.Column(db.String(10), primary_key=True)
    nama = db.Column(db.String(100))
    harga = db.Column(db.Integer)
    stok = db.Column(db.Integer)

class Transaksi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20))
    total = db.Column(db.Integer)
    diskon = db.Column(db.Integer)
    pajak = db.Column(db.Integer)
    grand_total = db.Column(db.Integer)

class DetailTransaksi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaksi_id = db.Column(db.Integer)
    kode_barang = db.Column(db.String(10))
    nama_barang = db.Column(db.String(100))
    harga = db.Column(db.Integer)
    qty = db.Column(db.Integer)
    subtotal = db.Column(db.Integer)

with app.app_context():
    db.create_all()

# AUTH 
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        email = request.form['email']

        if not userid.isalnum() or len(userid) < 6:
            return "UserID tidak valid"

        if len(password) < 8 or not any(c.isupper() for c in password):
            return "Password tidak valid"

        if not validasi_email(email):
            return "Email tidak valid"

        if User.query.get(userid):
            return "User sudah ada"

        user = User(userid=userid,password=password,email=email)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.get(request.form['userid'])

        if not user or user.password != request.form['password']:
            return "Login gagal"

        session['user'] = user.userid
        return redirect('/')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# CRUD
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')

    data = Barang.query.all()
    return render_template('index.html', data=data)

@app.route('/tambah', methods=['GET','POST'])
def tambah():
    if request.method == 'POST':
        kode = request.form['kode'].upper()
        nama = request.form['nama']

        if not kode.isalnum():
            return "Kode tidak valid"

        if not nama.replace(" ","").isalpha():
            return "Nama tidak valid"

        if Barang.query.get(kode):
            return "Sudah ada"

        barang = Barang(kode=kode,nama=nama,harga=int(request.form['harga']),stok=int(request.form['stok']))
        db.session.add(barang)
        db.session.commit()
        return redirect('/')

    return render_template('tambah.html')

@app.route('/delete/<kode>')
def delete(kode):
    b = Barang.query.get(kode)
    db.session.delete(b)
    db.session.commit()
    return redirect('/')

# TRANSAKSI
@app.route('/transaksi', methods=['GET','POST'])
def transaksi():
    data = Barang.query.all()

    if request.method == 'POST':
        total = 0
        total_qty = 0
        keranjang = []

        for b in data:
            qty = request.form.get(b.kode)
            if qty and qty.isdigit() and int(qty)>0:
                qty = int(qty)

                if qty > b.stok:
                    return "Stok tidak cukup"

                subtotal = b.harga * qty
                total += subtotal
                total_qty += qty
                keranjang.append((b,qty,subtotal))

        diskon = int(max(
            total*0.15 if total_qty>=10 else total*0.10 if total_qty>=5 else 0,
            total*0.20 if total>=500000 else total*0.10 if total>=200000 else 0
        ))

        setelah = total - diskon
        pajak = int(setelah*PPN)
        grand = int(setelah+pajak)

        trx = Transaksi(userid=session['user'],total=total,diskon=diskon,pajak=pajak,grand_total=grand)
        db.session.add(trx)
        db.session.flush()

        for b,qty,subtotal in keranjang:
            db.session.add(DetailTransaksi(
                transaksi_id=trx.id,
                kode_barang=b.kode,
                nama_barang=b.nama,
                harga=b.harga,
                qty=qty,
                subtotal=subtotal
            ))
            b.stok -= qty

        db.session.commit()

        return redirect('/riwayat')

    return render_template('transaksi.html', data=data)

@app.route('/riwayat')
def riwayat():
    data = Transaksi.query.filter_by(userid=session['user']).all()
    return render_template('riwayat.html', data=data)

# RUN 
if __name__ == '__main__':
    app.run(debug=True)
