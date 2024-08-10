from flask import session, redirect, url_for, request
from database import DataBase
from dateutil.relativedelta import relativedelta
from datetime import datetime

now = datetime.now().date()

def odeme_al(db, form, ogrenciId):
    dataG = fetch_genel_odemeler(db, ogrenciId)
    ogrenciAdSoyad = dataG["ogrenciAdSoyad"]
    odemeMiktari = form.odemeMiktari.data
    sonrakiOdemeTarihi = form.odemeTarihi.data
    odemeyiAlan = session["adSoyad"]
    odemeyiYapan = form.odemeyiYapan.data
    sorgu = "Insert Into odemeler (ogrenciId, ogrenciAdSoyad, odemeMiktari, sonrakiOdemeTarihi, odemeyiAlan, odemeyiYapan) Values (%s, %s, %s, %s, %s, %s)"
    values = (ogrenciId, ogrenciAdSoyad, odemeMiktari, sonrakiOdemeTarihi, odemeyiAlan, odemeyiYapan)
    db.execute(sorgu, values)
    toplam = 0
    dataO = fetch_odemeler(db, ogrenciId, 'islemTarihi')
    for d in dataO:
        toplam += d["odemeMiktari"]
    sorgu = f"Update genel_odemeler Set toplamOdenen = {toplam}, sonrakiOdemeTarihi = '{sonrakiOdemeTarihi}' Where ogrenciId = {ogrenciId}"
    db.execute(sorgu)
    return redirect(url_for("odeme_ogrenci", islem="odeme", id = ogrenciId))

def odeme_sil(db, ogrenciId):
    odemeId = int(request.form.get("odeme_sil")) #sil butonundan silinecek ödeme kayıt id sini alıyoruz
    db.delete('odemeler', 'id', odemeId)# seçilen ödeme silindi
    dataO = fetch_odemeler(db, ogrenciId, 'sonrakiOdemeTarihi')#öğrencinin ödemelerini liste olarak al
    toplam = 0#güncel toplam ödeneni hesaplamak için
    if dataO != False:#eğer liste boş değilse
        sonrakiOdemeTarihi = dataO[0]["sonrakiOdemeTarihi"]#güncel sonraki ödeme tarihi için sıralanmış listenin ilk sonrakiOdemeTarihini güncel olarak ekle
        for d in dataO:
            toplam += d["odemeMiktari"]#hesaplanan toplam ödenmiş
        sorgu = f"Update genel_odemeler Set toplamOdenen = {toplam}, sonrakiOdemeTarihi = '{sonrakiOdemeTarihi}' Where ogrenciId = {ogrenciId}"
        db.execute(sorgu)
    return redirect(url_for('odeme_ogrenci', islem='odeme', id=ogrenciId))

def odeme_sayfa_hazirla(db, ogrenciId):#bunu değiştir ödemeler tablosundan değil genel_odemelerden tarih al
    ogrenci = db.fetch_data(sorgu=None, values=None, tablo="ogrenciler", id = ogrenciId)
    genel_odeme = fetch_genel_odemeler(db, ogrenciId)
    odemeler = fetch_odemeler(db, ogrenciId, 'islemTarihi')
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
    #bu fonksiyon 2 parametre alır database obesi ve öğrenciId
    sorgu = f"Select * From genel_odemeler Where ogrenciId = {ogrenciId}"
    data = db.fetch_data(sorgu=sorgu, values=None, tablo=None)
    if data != False:#Eğer data tuple ı boş değilse
        return data[0]#Bu tauple ı ilk elmanını alarak döner. Yani tuple içindeki sözlük anahtar kelimeler ile direk kullanılabilir.
    return data 

def fetch_odemeler(db, ogrenciId, orderBy):
    #Bu fonksiyon 3 parametre alır kullanılacak database objesi, öğrenciId ve sıralanacak sütun
    sorgu = f"Select * From odemeler Where ogrenciId = {ogrenciId} Order By {orderBy} DESC"
    data = db.fetch_data(sorgu=sorgu, values=None, tablo=None)
    if data != False:#Eğer data boş değilse
        odemeler = []
        for d in data:
            odemeler.append(d)#Geriye dönen  data adlı tuple ı odemeler listeye çeivirir
        return odemeler
    else:
        return False


def odeme_tarih_tablosu(db):
    sorgu="Select * From genel_odemeler Order By sonrakiOdemeTarihi ASC"
    ogrenciler = db.fetch_data(sorgu=sorgu, values=None, tablo=None)#Öğrencilerin genel_odemeler tablosundaki verilerini tarihe göre sıralayarak çek
    if ogrenciler:
        ogrenciler = list(ogrenciler)
        for o in ogrenciler:
            if o['sonrakiOdemeTarihi'] > now:
                o['durum'] = 'table-success'
            elif o['sonrakiOdemeTarihi'] == now:
                o['durum'] = 'table-warning'
            elif o['sonrakiOdemeTarihi'] < now:
                o['durum'] = 'table-danger'
            else:
                o['durum'] = 'table-light'
    return ogrenciler

