from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, send_from_directory
from functools import wraps
from utlity import registeration, loginPrcs, create_url
from database import DataBase
from ogrenci import Ogrenci, ogrenciKaydet, ogrenci_search
from kulup import kulup_bilgi_ekle, kulup_bilgi_guncelle, kulup_bilgi_sil
from forms import OgrenciForm

gymsw = Flask(__name__)
gymsw.config['UPLOAD_FOLDER'] = "uploads/"
#Flash mesajlarının kullanımı için secret key
gymsw.secret_key = "mkrdmn"


db = DataBase(gymsw)


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
"""
@gymsw.route('/<path:filename>')
def uploaded_file(path):
    return send_from_directory(path)
"""

#Anasayfa; Başlıyor
@gymsw.route("/")
def index():
    return render_template("index.html")
#Anasayfa; Bitti


#Login Sayfası; Başlıyor
@gymsw.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        attempt = loginPrcs(db)
        if attempt == True:
            flash("Giriş başarılı","success")  
            return redirect(url_for("dashboard"))
        elif attempt == False:
            flash("Böyle bir kullanıcı bulunamadı","danger")
            return redirect(url_for("login"))
        elif attempt == "Sifre yanlis":
            flash("Şifreniz yanlış lütfen tekrar deneyin","danger")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")    
#Login Sayfası Bitti


#Logout; Başlıyor
@gymsw.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


#Register Sayfası; Başlıyor
@gymsw.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        return registeration(db)
    else:
        return render_template("register.html")
#Register Sayfası Bitti


#Dashboard -- Üye Girişi; Başlıyor
@gymsw.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
#Dashboard -- Üye Girişi Bitti


@gymsw.route("/dashboard/kulup", methods=["GET","POST"])
@login_required
def kulup():
    antrenorler = db.get_from_db("antrenor")
    branslar = db.get_from_db("branslar")
    gruplar = db.get_from_db("gruplar")
    salonlar = db.get_from_db("salonlar")
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
    branslar = db.get_from_db("branslar")
    gruplar = db.get_from_db("gruplar")
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
    branslar = db.get_from_db("branslar")
    gruplar = db.get_from_db("gruplar")
    return render_template("/dashboard/ogrenci_listesi.html", branslar=branslar, gruplar=gruplar, ogrenciler=ogrenciler)

@gymsw.route("/dashboard/ogrenci_islem/<string:islem>/<int:id>")
@login_required
def ogrenci_islem(islem, id):
    if islem == "delete":
        return redirect(url_for("ogrenci_listesi"))
    if islem == "edit":
        form = OgrenciForm(request.form)
        ogrenci = db.fetch_data(sorgu=None, values=None, tablo="ogrenciler", id=id)
        #ogrenci = db.get_from_db_id("ogrenciler", id)
        return render_template("/dashboard/ogrenci_edit.html", form=form, ogrenci = ogrenci)



if __name__ == "__main__":
    gymsw.run(debug=True)
