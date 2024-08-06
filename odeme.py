from flask import session, redirect, url_for, request
from database import DataBase
from dateutil.relativedelta import relativedelta
from datetime import datetime

def odeme_al(db, form, ogrenciId):
    dataG = fetch_genel_odemeler(db, ogrenciId)
    ogrenciId = ogrenciId
    ogrenciAdSoyad = dataG["ogrenciAdSoyad"]
    odemeMiktari = form.odemeMiktari.data
    sonrakiOdemeTarihi = form.odemeTarihi.data
    odemeyiAlan = session["adSoyad"]
    odemeyiYapan = form.odemeyiYapan.data
    sorgu = "Insert Into odemeler (ogrenciId, ogrenciAdSoyad, odemeMiktari, sonrakiOdemeTarihi, odemeyiAlan, odemeyiYapan) Values (%s, %s, %s, %s, %s, %s)"
    values = (ogrenciId, ogrenciAdSoyad, odemeMiktari, sonrakiOdemeTarihi, odemeyiAlan, odemeyiYapan)
    db.execute(sorgu, values)
    toplam = 0
    dataO = fetch_odemeler(db, ogrenciId)
    for d in dataO:
        toplam += d["odemeMiktari"]
    sorgu = f"Update genel_odemeler Set toplamOdenen = {toplam} Where ogrenciId = {ogrenciId}"
    db.execute(sorgu)
    return redirect(url_for("odeme_ogrenci", islem="odeme", id = ogrenciId))

def odeme_sil(db, ogrenciId):
    odemeId = int(request.form.get("odeme_sil")) #sil butonundan silinecek ödeme kayıt id sini alıyoruz
    db.delete('odemeler', 'id', odemeId)
    dataO = fetch_odemeler(db, ogrenciId)
    toplam = 0
    if dataO != False:
        for d in dataO:
            toplam += d["odemeMiktari"]
        sorgu = f"Update genel_odemeler Set toplamOdenen = {toplam} Where ogrenciId = {ogrenciId}"
        db.execute(sorgu)
    return redirect(url_for('odeme_ogrenci', islem='odeme', id=ogrenciId))

def odeme_sayfa_hazirla(db, ogrenciId):#bunu değiştir ödemeler tablosundan değil genel_odemelerden tarih al
    ogrenci = db.fetch_data(sorgu=None, values=None, tablo="ogrenciler", id = ogrenciId)
    genel_odeme = fetch_genel_odemeler(db, ogrenciId)
    odemeler = fetch_odemeler(db, ogrenciId)
    if odemeler != False: #sonrakiOdemeTarihi için forma gönderilecek tarih
        tarih = odemeler[0]["sonrakiOdemeTarihi"] + relativedelta(months=1)
    else:
        tarih = ogrenci["ilkOdemeTarihi"] + relativedelta(months=1)
    data=[ogrenci, genel_odeme, odemeler, tarih]
    return data

def list_odeme(db):
    #Bu fonksiyon dashboard sayfasında ödemesi gelen öğrencileri listeleyecek
    sorgu = "Select * From odemeler ORDER BY ogrenciId, sonrakiOdemeTarihi DESC"
    odemeler = db.fetch_data(sorgu=sorgu, values=None, tablo=None)
    


def fetch_genel_odemeler(db, ogrenciId):
    sorgu = f"Select * From genel_odemeler Where ogrenciId = {ogrenciId}"
    data = db.fetch_data(sorgu=sorgu, values=None, tablo=None)
    return data[0]

def fetch_odemeler(db, ogrenciId):
    sorgu = f"Select * From odemeler Where ogrenciId = {ogrenciId} Order By islemTarihi DESC"
    data = db.fetch_data(sorgu=sorgu, values=None, tablo=None)
    if data != False:
        odemeler = []
        for d in data:
            odemeler.append(d)
        return odemeler
    else:
        return False
