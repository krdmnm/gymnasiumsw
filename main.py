from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, send_from_directory
from functools import wraps
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utlity import registeration, loginPrcs, create_url
from database import DataBase
from ogrenci import Ogrenci, ogrenciKaydet, ogrenciEdit, ogrenci_search, ogrenci_goruntule
from kulup import kulup_bilgi_ekle, kulup_bilgi_guncelle, kulup_bilgi_sil
from forms import OgrenciForm, OdemeForm, LoginForm, RegisterForm
from odeme import odeme_sayfa_hazirla, odeme_al, odeme_sil, list_odeme, odeme_tarih_tablosu

gymsw = Flask(__name__)
gymsw.config['UPLOAD_FOLDER'] = "uploads/"
#Flash mesajlarının kullanımı için secret key
gymsw.secret_key = "mkrdmn"

now = datetime.now().date()
db = DataBase(gymsw)
"""
@gymsw.teardown_appcontext
def close_database():
    db.close_db()
"""
#Kullanıcı Session Kontrolü İçin Decorator; Başlıyor
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #session içinde logged_in anahtarını kontrol edelim;
        if "logged_in" in session and session["aktivasyon"]:
            return f(*args, **kwargs)
        else:
            #Burada giriş yapılmadı. Giriş sayfasına yönlendirip flash mesajı verelim.
            flash("Sayfaya erişmek için giriş yapmalısınız", "danger")
            return redirect(url_for("login"))
    return decorated_function
##Kullanıcı Session Kontrolü İçin Decorator; Bitti

#Burada kullanıcı loginse ona göre DataBase konfigürasyonu yapalım
@gymsw.before_request
def dbConfigure():
    if "logged_in" in session:
        db.configure_db(session["dbAdi"], session["dbUser"], session["dbPassword"])
    else:
        db.configure_db("maindb", "root", "")


#Anasayfa; Başlıyor
@gymsw.route("/")
def index():
    return render_template("index.html")
#Anasayfa; Bitti


#Login Sayfası; Başlıyor
@gymsw.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        attempt = loginPrcs(db, form)
        if attempt == True:
            flash("Giriş başarılı","success")  
            return redirect(url_for("dashboard"))
        elif attempt == False:
            flash("Böyle bir kullanıcı bulunamadı","danger")
            return redirect(url_for("login"))
        elif attempt == "Sifre yanlis":
            flash("Şifreniz yanlış lütfen tekrar deneyin","danger")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)    
#Login Sayfası Bitti


#Logout; Başlıyor
@gymsw.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


#Register Sayfası; Başlıyor
@gymsw.route("/register", methods = ["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        return registeration(db, form)
    return render_template("register.html", form=form)
#Register Sayfası Bitti


#Dashboard -- Üye Girişi; Başlıyor
@gymsw.route("/dashboard")
@login_required
def dashboard():
    ogrenciler = odeme_tarih_tablosu(db)
    return render_template("dashboard.html", ogrenciler = ogrenciler)
#Dashboard -- Üye Girişi Bitti


@gymsw.route("/dashboard/kulup", methods=["GET","POST"])
@login_required
def kulup():
    antrenorler = db.fetch_data(sorgu=None, values=None, tablo="antrenor")
    branslar = db.fetch_data(sorgu=None, values=None, tablo="branslar")
    gruplar = db.fetch_data(sorgu=None, values=None, tablo="gruplar")
    salonlar = db.fetch_data(sorgu=None, values=None, tablo="salonlar")
    return render_template("/dashboard/kulup.html", antrenorler=antrenorler, branslar = branslar, gruplar = gruplar, salonlar = salonlar)

@gymsw.route("/dashboard/kulup_islem/<string:islem>/<string:tablo>/<int:id>", methods=["POST", "GET"])
@login_required
def kulup_islem(islem, tablo, id):
    if islem == "ekle":
        kulup_bilgi_ekle(db, tablo)
    if islem == "edit":
        kulup_bilgi_guncelle(db, tablo, id)
    if islem == "delete":
        kulup_bilgi_sil(db, tablo, id)
    return redirect(url_for("kulup"))

            
@gymsw.route("/dashboard/ogrenci_kaydet", methods=["GET", "POST"])
@login_required
def ogrenci_kaydet():
    form = OgrenciForm()
    if request.method=="POST":
        return ogrenciKaydet(db, form)
    branslar = db.fetch_data(sorgu=None, values=None, tablo="branslar")
    gruplar = db.fetch_data(sorgu=None, values=None, tablo="gruplar")
    if branslar:
        form.ogrenciBrans.choices=[brans['bransAdi'] for brans in branslar]
    else:
        form.ogrenciBrans.choices=["Henüz branş eklenmemiş"]
    if gruplar:
        form.ogrenciGrup.choices=[grup['grupAdi'] for grup in gruplar]
    else:
        form.ogrenciGrup.choices=["Henüz grup eklenmemiş"]
    flash("* olan alanları doldurmak zorundasınız", "warning")
    return render_template("/dashboard/ogrenci_kaydet.html",form=form, branslar=branslar, gruplar=gruplar)

@gymsw.route("/dashboard/ogrenci_listesi", methods=["POST","GET"])
@login_required
def ogrenci_listesi():
    if request.method=="POST":
        return create_url("ogrenci_list_filter")
    branslar = db.fetch_data(sorgu=None, values=None, tablo="branslar", id='id')
    gruplar = db.fetch_data(sorgu=None, values=None, tablo="gruplar", id='id')
    ogrenciler = db.fetch_data(sorgu=None, values=None, tablo="ogrenciler", id='id')
    return render_template("/dashboard/ogrenci_listesi.html", ogrenciler = ogrenciler, branslar=branslar, gruplar=gruplar)

@gymsw.route("/dashboard/ogrenci_listesi/filter/<string:brans>/<string:grup>/<string:searchBy>/<string:keyword>", methods=["GET", "POST"])
@login_required
def ogrenci_list_filter(brans, grup, searchBy, keyword):
    if request.method=="POST":
        return create_url("ogrenci_list_filter")
    ogrenciler = ogrenci_search(db, brans, grup, searchBy, keyword)
    if ogrenciler == False:
        flash("Arama bulunamadı", "warning")
        return redirect(url_for("ogrenci_listesi"))
    branslar = db.fetch_data(sorgu = None, values=None, tablo="branslar")
    gruplar = db.fetch_data(sorgu = None, values=None, tablo="gruplar")
    return render_template("/dashboard/ogrenci_listesi.html", branslar=branslar, gruplar=gruplar, ogrenciler=ogrenciler)

@gymsw.route("/dashboard/ogrenci_islem/<string:islem>/<int:id>", methods=["POST", "GET"])
@login_required
def ogrenci_islem(islem, id):
    form = OgrenciForm()
    if request.method == "POST":
        if islem == 'duzenle':
            return ogrenciEdit(db, form, id)
        if islem == 'odeme':
            pass    
    if islem == "delete":
        db.delete("ogrenciler", "id", id)
        flash("Öğrenci silindi", "success")
        return redirect(url_for("ogrenci_listesi"))
    if islem == "goruntule":
        data = ogrenci_goruntule(db, id, form)
        return render_template("/dashboard/ogrenci.html", ogrenci=data[0], form=data[3])

@gymsw.route("/dashboard/odeme_ogrenci/<string:islem>/<int:id>", methods=["POST", "GET"])
@login_required
def odeme_ogrenci(islem, id):
    form = OdemeForm()
    if request.method == "POST":
        if islem == "odeme_al":
            return odeme_al(db, form, id)
        if islem == "odeme_sil":
            return odeme_sil(db, id)
    data = odeme_sayfa_hazirla(db, id)
    form.fill_form(data[3])
    list_odeme(db)
    return render_template("/dashboard/odeme_ogrenci.html", form = form, ogrenci=data[0], genelOdeme=data[1], odemeler = data[2])

@gymsw.route("/dashboard/etkinlik")
@login_required
def etkinlik():
    events = db.fetch_data(sorgu=None, values=None, tablo="events")
    return render_template("/dashboard/etkinlik.html")

if __name__ == "__main__":
    gymsw.run(debug=True)
