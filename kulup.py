from flask import Flask, render_template, flash, redirect, url_for, session, request
from database import MainDB
def kulup_bilgi_ekle(db, tablo):
    formData = request.form.to_dict()
    columns = db.get_columns(tablo)
    columns = [column["Field"] for column in columns]
    del columns[0]
    #şimdi verileri filtreleyelim.
    filteredData = {key: value for key, value in formData.items() if key in columns}
    #sütun adlarının sonuna sorgu için virgül ve boşluk ekleyelim.
    column_names = ", ".join(filteredData.keys())
    #%s takılarını ayarlayalım
    placeholders = ", ".join(["%s"]*len(filteredData))
    #sorguyu hazırlayalım.
    sorgu = f"Insert Into {tablo} ({column_names}) Values ({placeholders})"
    values = tuple(filteredData.values())
    db.execute(sorgu, values)
    """
    if tablo == "antrenor":
        sorgu = "Insert Into users (adSoyad, userName, password, kulupAdi, aktivasyon, isAdmin, isSuperUser, dbAdi, dbUser, dbPassword, kayitTarihi, lisansSuresi, lisansTarihi)Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values=(filteredData["antrenorAdSoyad"], filteredData["antrenorUserName"], filteredData["antrenorPassword"], session["kulup"], session["aktivasyon"], False, False, session["dbAdi"], session["dbUser"], session["dbPassword"], session["kayitTarihi"], session["lisansSuresi"], session["lisansTarihi"])
        db.close_db()
        try:
            mdb = MainDB(app)
        except Exception as e:
            flash("Hata: " + str(e), "danger")
            return redirect(url_for("index"))
        mdb.execute(sorgu, values)
        mdb.close_db()
        print("******columns***********")
        print(columns)
        print("******filteredData************")
        print(filteredData)
        print("*****Sorgu*********")
        print(sorgu)
        print("*******Values********")
        print(values)
    """


    
def kulup_bilgi_guncelle(db, tablo, id):
    formData = request.form.to_dict()
    columns = db.get_columns(tablo)
    columns = [column["Field"] for column in columns]
    del columns[0]
    values = [formData[column] for column in columns if column in formData]
    values = tuple(values)
    set_clause = ", ".join(f"{column} = %s" for column in columns)
    sorgu = f"Update {tablo} Set {set_clause} Where id = {id}"
    db.execute(sorgu, values)



def kulup_bilgi_sil(db, tablo, id):
    db.delete(tablo, "id", id)
    flash("Silme işlemi başarılı")


