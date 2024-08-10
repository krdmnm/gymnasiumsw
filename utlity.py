from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from database import DataBase
import re
import os

def registeration(db, form):
    adSoyad = form.adSoyad.data
    telefon = form.telefon.data
    ePosta = form.ePosta.data
    userName = form.userName.data
    password = form.password.data
    dbPassword = createDbPassword(password)
    password = generate_password_hash(password)
    kulupAdi = form.kulupAdi.data
    aktivasyon = True
    isAdmin = True
    isSuperUser = False
    dbAdi = createDbName(kulupAdi)
    dbUser = createDbUsername(ePosta)
    
    if db.control_value("ePosta", ePosta) and db.control_value("userName", userName):
        #Kullanıcıyı maindb veritabanına kayıt edelim.
        sorgu = "Insert Into users (adSoyad, telefon, ePosta, userName, password, kulupAdi, aktivasyon, isAdmin, isSuperUser, dbAdi, dbUser, dbPassword) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (adSoyad, telefon, ePosta, userName, password, kulupAdi, aktivasyon, isAdmin, isSuperUser, dbAdi, dbUser, dbPassword)
        try:
            db.execute(sorgu, values)
        except Exception as e:
            flash("Kullanıcı hesabınız kaydedilirken sorun oluştu. Lütfen sistem yöneticisine bildirin. Hata Kodu: " + str(e), "danger")
        try:
            db.create_db(dbAdi)
            db.create_user(dbAdi, dbUser, dbPassword)
        except Exception as e:
            flash("Veri tabanınız yapılandırılamadı. Lütfen sistem yöneticisine bildirin. Hata Kodu: " + str(e), "danger")
        db.change_db(dbAdi)
        try:
            db.create_antrenor()
            db.create_ogrenciler()
            db.create_branslar()
            db.create_gruplar()
            db.create_salonlar()
            db.create_odemeler()
            db.create_genelOdemeler()
            db.create_events()
        except Exception as e:
            flash("Tablolar yapılandırılamadı. Lütfen sistem yöneticisine bildirin. Hata Kodu: " + str(e), "danger")
        try:
            db.triggers_for_odemeler()
            db.triggers_for_genelOdemeler()
        except Exception as e:
            flash("Tablolar tetiklendirilemedi. Lütfen sistem yöneticisine bildirin. Hata Kodu: " + str(e), "danger")
        create_folders(dbAdi)
        flash("Başarıyla Kayıt Oldunuz", "success")
        return redirect(url_for("index"))
    else:
        flash("Kaydınız gerçekleşmedi. Bu E-Posta adresi veya kullanıcı adı kullanılıyor", "danger")
        return redirect(url_for("register"))


def loginPrcs(db, form):
    ePosta = form.userName.data
    password = form.password.data
    if  (data := db.login_db(ePosta)) == False:
        return False
    else:
        if check_password_hash(data["password"], password):
            session["id"] = data["id"]
            session["adSoyad"] = data["adSoyad"]
            session["kulup"] = data["kulupAdi"]
            session["dbAdi"] = data["dbAdi"]
            session["dbUser"] = data["dbUser"]
            session["dbPassword"] = data["dbPassword"]
            session["aktivasyon"] = data["aktivasyon"]
            session["isAdmin"] = data["isAdmin"]
            session["isSuperUser"] = False
            session["kayitTarihi"] = data["kayitTarihi"]
            session["lisansSuresi"] = data["lisansSuresi"]
            session["lisansTarihi"] = data["lisansTarihi"]
            session["logged_in"] = True
            return True
        else:
            return "Sifre yanlis"



def createDbName(isim):
    # Boşlukları çıkar veya alt çizgi ile değiştir
    yeni_isim = re.sub(r'\s+', '_', isim)
    #Tüm harfleri küçük yap
    yeni_isim = yeni_isim.lower()
    #Türkçe karakterleri dönüştür
    yeni_isim = yeni_isim.replace('ç', 'c').replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ş','s').replace('ğ','g')
    #Uygun olmayan karakterleri temizle
    yeni_isim = re.sub(r'[^a-z0-9_]', '', yeni_isim)
    return str(yeni_isim)



def createDbUsername(email):
    # E-posta adresinden temizleme
    temizEposta = re.sub(r'[^a-zA-Z0-9]', '', email)
    # Kullanıcı adını sınırlama
    dbUserName = temizEposta[:16]
    return dbUserName



def createDbPassword(password):
    temizPassword = password.replace(' ', '')
    temizPassword = re.sub(r'[^a-zA-Z0-9]', '', password)
    temizPassword = temizPassword.lower()
    temizPassword = temizPassword.replace('ç', 'c').replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ş','s').replace('ğ','g')
    temizPassword = temizPassword[:16]
    return temizPassword

#Registiration esnasında oluşturulacak ilk klasörler
def create_folders(folderName):
        try:
            klasor = os.path.join('uploads', folderName)
            if not os.path.exists(klasor):
                os.makedirs(klasor)
        except OSError as e:
            mesaj = "Belirtilen klasör oluşturulamadı " + folderName + " Hata Kodu: " + str(e)
            flash(mesaj, "danger")
        try:
            foto = os.path.join(klasor,'foto')
            if not os.path.exists(foto):
                os.makedirs(foto)
        except OSError as e:
            mesaj = "Belirtilen klasör oluşturulamadı " + 'foto' + " Hata Kodu: " + str(e)
            flash(mesaj, "danger")
        try:
            yedek = os.path.join(klasor, 'yedek')
            if not os.path.exists(yedek):
                os.makedirs(yedek)
        except OSError as e:
            mesaj = "Belirtilen klasör oluşturulamadı " + 'yedek' + " Hata Kodu: " + str(e)
            flash(mesaj, "danger")
        try:
            log = os.path.join(klasor, 'logs')
            if not os.path.exists(log):
                os.makedirs(log)
        except OSError as e:
            mesaj = "Belirtilen klasör oluşturulamadı " + 'logs' + " Hata Kodu: " + str(e)
            flash(mesaj, "danger")


#logs yedekler için tarihe bağlı oluşturulacak alt klasörler için.
def create_folder(folderName, subFolder):
    new_folder = os.path.join('uploads', session["dbAdi"], subFolder, folderName)
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

def create_url(function_name):
    formData = request.form.to_dict()
    if formData['keyword'] == "":
        formData["keyword"] = "*"
    created_url = url_for(function_name, brans=formData['branslar'], grup=formData['gruplar'], searchBy=formData['searchBy'], keyword=formData['keyword'])
    return redirect(created_url)


def save_file(file, file_path, fileName):
    #Önce root olmadan dosyanın yolunu yapalım
    folder = os.path.join('uploads', session["dbAdi"], file_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    filePath = os.path.join(folder, fileName)
    #Dosyayı kaydettik
    file.save(filePath)
    #işaretleri değiştirelim
    filePath = filePath.replace("\\", "/")
    #Dosyanın tam yolunu url root ile ayarlayalım ve veri tabanına öyle kaydetsin
    fullPath = os.path.join(request.url_root, filePath)
    return fullPath
