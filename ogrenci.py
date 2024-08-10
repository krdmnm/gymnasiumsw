from flask import Flask, render_template, flash, redirect, url_for, request, session, jsonify
from flask_wtf.file import FileField, FileAllowed
import os
from werkzeug.utils import secure_filename
from database import DataBase
from datetime import datetime
from utlity import save_file
from odeme import fetch_genel_odemeler, fetch_odemeler

class Ogrenci():
    def __init__(self, sozluk) -> None:
        self.id = sozluk["id"] 
        self.foto = sozluk["ogrenciFoto"] if sozluk["ogrenciFoto"] is not None else "default.png"
        self.tc = sozluk["ogrenciTC"] if sozluk["ogrenciTC"] is not None else "00000000000"
        self.ad = sozluk["ogrenciAd"] if sozluk["ogrenciAd"] is not None else "-"
        self.soyad = sozluk["ogrenciSoyad"] if sozluk["ogrenciSoyad"] is not None else "-"
        self.telefon = sozluk["ogrenciTelefon"] if sozluk["ogrenciTelefon"] is not None else "-"
        self.yas = sozluk["ogrenciYas"] if sozluk["ogrenciYas"] is not None else 0
        self.dogumTarihi = sozluk["ogrenciDogumTarihi"] if sozluk["ogrenciDogumTarihi"] is not None else "-"
        self.brans = sozluk["ogrenciBrans"] if sozluk["ogrenciBrans"] is not None else "-"
        self.grup = sozluk["ogrenciGrup"] if sozluk["ogrenciGrup"] is not None else "-"
        self.veliAd = sozluk["veliAd"] if sozluk["veliAd"] is not None else "-"
        self.veliTelefon = sozluk["veliTelefon"] if sozluk["veliTelefon"] is not None else "-"
        self.veli2Ad = sozluk["veli2Ad"] if sozluk["veli2Ad"] is not None else "-"
        self.veli2Telefon = sozluk["veli2Telefon"] if sozluk["veli2Telefon"] is not None else "-"
        self.ilkOdemeTarihi = sozluk["ilkOdemeTarihi"] if sozluk["kayitTarihi"] is not None else "-"
        self.toplamODeme = sozluk["toplamOdeme"] if sozluk["toplamOdeme"] is not None else 0.0
        


def ogrenciKaydet(db, form):
    try:
        file = form.ogrenciFoto.data
        ogrenciAd = form.ogrenciAd.data
        ogrenciSoyad = form.ogrenciSoyad.data
        if file:
            file_extension = os.path.splitext(file.filename)[1] #Dosya uzantısını alıp dosya adına ekleyeceğiz
            fotoname = secure_filename(f"{ogrenciAd}_{ogrenciSoyad}{file_extension}")
            ogrenciFoto = save_file(file, 'foto', fotoname)
        else:
            ogrenciFoto = None
        ogrenciTC = form.ogrenciTC.data
        ogrenciTelefon = form.ogrenciTelefon.data
        ogrenciYas = form.ogrenciYas.data
        ogrenciDogumTarihi = form.ogrenciDogumTarihi.data
        ogrenciBrans = form.ogrenciBrans.data
        ogrenciGrup = form.ogrenciGrup.data
        veliAd = form.veliAd.data
        veliTelefon = form.veliTelefon.data
        veli2Ad = form.veli2Ad.data
        veli2Telefon = form.veli2Telefon.data
        toplamOdeme = form.toplamOdeme.data
        ilkOdemeTarihi = form.ilkOdemeTarihi.data
        sorgu = "Insert Into ogrenciler (ogrenciFoto, ogrenciTC, ogrenciAd, ogrenciSoyad, ogrenciTelefon, ogrenciYas, ogrenciDogumTarihi, ogrenciBrans, ogrenciGrup, veliAd, veliTelefon, veli2Ad, veli2Telefon, ilkOdemeTarihi, toplamOdeme) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values =(ogrenciFoto, ogrenciTC, ogrenciAd, ogrenciSoyad, ogrenciTelefon, ogrenciYas, ogrenciDogumTarihi, ogrenciBrans, ogrenciGrup, veliAd, veliTelefon, veli2Ad, veli2Telefon, ilkOdemeTarihi, toplamOdeme)
        db.execute(sorgu, values)
        flash(ogrenciAd + " " + ogrenciSoyad + " " + "başarıyla kaydedildi", "success")
        return redirect(url_for("ogrenci_kaydet"))  
    except Exception as e:
        return jsonify({"error": str(e)}), 50
    """    except Exception as e:
        flash("Hata Kodu: ", e)
        return redirect(url_for("ogrenci_kaydet"))"""


def ogrenciEdit(db, form, id):
    ogrenciAd=form.ogrenciAd.data
    ogrenciSoyad = form.ogrenciSoyad.data
    file = form.ogrenciFoto.data
    if file:
        file_extension = os.path.splitext(file.filename)[1]
        fotoname = secure_filename(f"{ogrenciAd}_{ogrenciSoyad}{file_extension}")
        ogrenciFoto = save_file(file,'foto', fotoname)
    else:
        ogrenci = db.fetch_data(sorgu=None, values=None, tablo='ogrenciler')
        ogrenciFoto = ogrenci[0]['ogrenciFoto']
    ogrenciTC = form.ogrenciTC.data
    ogrenciTelefon = form.ogrenciTelefon.data
    ogrenciYas = form.ogrenciYas.data
    ogrenciDogumTarihi = form.ogrenciDogumTarihi.data
    ogrenciBrans = form.ogrenciBrans.data
    ogrenciGrup = form.ogrenciGrup.data
    veliAd = form.veliAd.data
    veliTelefon = form.veliTelefon.data
    veli2Ad = form.veli2Ad.data
    veli2Telefon = form.veli2Telefon.data
    ilkOdemeTarihi = form.ilkOdemeTarihi.data
    toplamOdeme = form.toplamOdeme.data
    values = (ogrenciFoto, ogrenciTC, ogrenciAd, ogrenciSoyad, ogrenciTelefon, ogrenciYas, ogrenciDogumTarihi, ogrenciBrans, ogrenciGrup, veliAd, veliTelefon, veli2Ad, veli2Telefon, ilkOdemeTarihi, toplamOdeme)
    columns = db.get_columns("ogrenciler")
    columns = [column["Field"] for column in columns]
    del columns[0]
    del columns[13]
    print("*******columns********")
    print(columns)
    db.update_db("ogrenciler", columns, values, id)
    flash("Öğrenci bilgileri düzenlendi", "success")
    return redirect(url_for("ogrenci_islem", islem="goruntule", id=id))

    
def ogrenci_search(db, brans, grup, searchBy, keyword):
    sorgu = "Select * From ogrenciler Where 1=1"
    
    if brans != "ogrenciBrans":
        sorgu += f" And ogrenciBrans = '{brans}'"

    if grup != "ogrenciGrup":
        sorgu += f" And ogrenciGrup = '{grup}'"

    if keyword != "*":
        sorgu += f" And {searchBy} Like '%{keyword}%'"
    ogrenciler = db.fetch_data(sorgu=sorgu, values=None, tablo=None, id='id')
    return ogrenciler

def ogrenci_goruntule(db, ogrenciId, form):
    ogrenci = db.fetch_data(sorgu=None, values=None, tablo="ogrenciler", id=ogrenciId)
    genelOdeme = fetch_genel_odemeler(db, ogrenciId)#Veri varsa tuple olacak
    odemeler = fetch_odemeler(db, ogrenciId, 'islemTarihi') # Veri varsa liste olacak tuple değil
    branslar = db.fetch_data(sorgu=None, values=None, tablo='branslar')
    gruplar = db.fetch_data(sorgu=None, values=None, tablo='gruplar')
    if branslar:
        form.ogrenciBrans.choices=[brans["bransAdi"] for brans in branslar]
    if gruplar:
        form.ogrenciGrup.choices=[grup['grupAdi'] + " / " + grup['grupBransi'] for grup in gruplar]
    form.fill_form(ogrenci)
    data = [ogrenci, genelOdeme, odemeler, form]
    return data