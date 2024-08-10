from flask_mysqldb import MySQL
from flask import flash


class DataBase:
    def __init__(self, app):
        self.app = app
        self.mysql = MySQL(self.app)

    def configure_db(self, dbAdi, dbUser, dbPassword):
        self.app.config["MYSQL_HOST"] = "localhost"
        self.app.config["MYSQL_USER"] = dbUser
        self.app.config["MYSQL_PASSWORD"] = dbPassword
        self.app.config["MYSQL_CURSORCLASS"] = "DictCursor"
        self.app.config["MYSQL_DB"] = dbAdi
        #self.mysql.init_app(self.app)

    def get_mysql(self):
        return self.mysql
    
    def close_db(self, exception=None):
        if hasattr(self, "mysql") and self.mysql.connection:
            self.mysql.connection.close()

    def get_columns(self, table):
        self.cursor = self.mysql.connection.cursor()
        sorgu = f"Show Columns From {table}"
        self.cursor.execute(sorgu)
        columns = self.cursor.fetchall()
        self.cursor.close()
        return columns

    def get_from_db(self, tablo):
        self.cursor = self.mysql.connection.cursor()
        sorgu = f"Select * From {tablo}"
        result = self.cursor.execute(sorgu)
        print("*********get_from_db*************")
        print(result)
        print("*********get_from_db*************")
        if result > 0:
            values = self.cursor.fetchall()
            self.cursor.close()
            return values
        else:
            self.cursor.close()
            return False
        
    def get(self, sorgu, values):
        #Veri tabanından veri çekmek için -- utility-- search_and_filter fonksiyonunda
        self.cursor = self.mysql.connection.cursor()
        result = self.cursor.execute(sorgu, values)
        if result > 0:
            data = self.cursor.fetchall()
            self.cursor.close()
            return data
        else:
            self.cursor.close()
            return False
    def get_without_values(self, sorgu):
        #Veri tabanından veri çekmek için -- utility-- search_and_filter fonksiyonunda
        self.cursor = self.mysql.connection.cursor()
        result = self.cursor.execute(sorgu)
        if result > 0:
            data = self.cursor.fetchall()
            self.cursor.close()
            return data
        else:
            self.cursor.close()
            return False


    def get_from_db_id(self, tablo, id):
        self.cursor = self.mysql.connection.cursor()
        sorgu = f"Select * From {tablo} Where id = {id}"
        result = self.cursor.execute(sorgu)
        if result > 0:
            values = self.cursor.fetchone()
            self.cursor.close()
            return values
        else:
            self.cursor.close()
            return False

    def fetch_data(self, sorgu=None, values=None, tablo=None, id = None):
        self.cursor = self.mysql.connection.cursor()
        if sorgu!=None:
            result = self.cursor.execute(sorgu, values or [])
            if result > 0:
                values = self.cursor.fetchall()
                self.cursor.close()
                return values
            self.cursor.close()
            return False
        else:
            sorgu = f"Select * From {tablo} where id = {id}"
            result = self.cursor.execute(sorgu)
            if result > 0:
                if id != 'id':
                    values = self.cursor.fetchone()
                else:
                    values = self.cursor.fetchall()
                self.cursor.close()
                return values
            self.cursor.close()
            return False

    def execute_db(self, sorgu, values):
        self.cursor = self.mysql.connection.cursor()
        self.cursor.execute(sorgu, values)
        lastID = self.cursor.lastrowid
        self.mysql.connection.commit()
        self.cursor.close()
        #return lastID

    def exec_db(self, sorgu):
        self.cursor = self.mysql.connection.cursor()
        self.cursor.execute(sorgu)
        self.mysql.connection.commit()
        self.cursor.close()

    def delete_from_table(self, table, column, value):
        try:
            self.cursor = self.mysql.connection.cursor()
            sorgu = f"Delete From {table} Where {column} = {value}"
            self.cursor.execute(sorgu)
            self.mysql.connection.commit()
        except Exception as e:
            flash("Silme işlemi başarısız oldu", "danger")
        finally:
            self.cursor.close()

    def update_db(self, tablo, columns, values, id):
        self.cursor = self.mysql.connection.cursor()
        sorgu = f"Update {tablo} Set "
        sayac = 1
        for column, value in zip(columns, values):
            sayac += 1
            sorgu += f"{column} = '{value}'"
            if sayac <= len(columns):
                sorgu += ", "
        sorgu += f" Where id = {id}"
        self.cursor.execute(sorgu)
        self.mysql.connection.commit()
        self.cursor.close()

    def update_antrenor(self, values):
        self.cursor = self.mysql.connection.cursor()
        sorgu = "Update antrenor Set antrenorAdSoyad = %s, antrenorUserName = %s, antrenorPassword = %s Where id = %s"
        self.cursor.execute(sorgu, values)
        self.mysql.connection.commit()
        self.cursor.close()

    def create_db(self, value):
        #utlity.py --- registeration()
        self.cursor = self.mysql.connection.cursor()
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {value}")
        self.mysql.connection.commit()
        self.cursor.close()
    
    def login_db(self, ePosta):
        self.cursor = self.mysql.connection.cursor()
        sorgu = "Select * From users where ePosta = %s"
        result = self.cursor.execute(sorgu, (ePosta,))
        if result >0:
            data = self.cursor.fetchone()
            self.cursor.close()
            return data
        else:
            self.cursor.close()
            return False
    
    def create_user(self, dbAdi, dbUser, dbPassword):
        self.cursor = self.mysql.connection.cursor()
        sorguForUser = "Create User %s@'localhost' Identified by %s"
        self.cursor.execute(sorguForUser, (dbUser, dbPassword))
        sorguForPrivileges = f"GRANT ALL PRIVILEGES ON {dbAdi}.* TO {dbUser}@'localhost'"
        self.cursor.execute(sorguForPrivileges)
        self.mysql.connection.commit()
        self.cursor.close()

    def change_db(self, dbAdi):
        sorgu = f"Use {dbAdi}"
        self.cursor = self.mysql.connection.cursor()
        self.cursor.execute(sorgu)
        self.mysql.connection.commit()
        self.cursor.close()

    def control_value(self, column, value):
        self.cursor =self.mysql.connection.cursor()
        sorgu = f"Select {column} from users Where {column} = %s"
        result = self.cursor.execute(sorgu, (value,))
        if result > 0:
            self.cursor.close()
            return False
        else:
            self.cursor.close()
            return True
        
    def create_ogrenciler(self):
        self.cursor = self.mysql.connection.cursor()
        sorgu = '''CREATE TABLE IF NOT EXISTS ogrenciler (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ogrenciFoto TEXT,
            ogrenciTC VARCHAR(11),
            ogrenciAd VARCHAR(50) NOT NULL,
            ogrenciSoyad VARCHAR(50) NOT NULL,
            ogrenciTelefon VARCHAR(50),
            ogrenciYas INT,
            ogrenciDogumTarihi DATE,
            ogrenciBrans VARCHAR(50),
            ogrenciGrup VARCHAR(50),
            veliAd VARCHAR(100) NOT NULL,
            veliTelefon VARCHAR(50) NOT NULL,
            veli2Ad VARCHAR (50),
            veli2Telefon VARCHAR(50),
            kayitTarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            toplamOdeme DECIMAL(10, 2)
        )'''
        self.cursor.execute(sorgu)
        self.mysql.connection.commit()
        self.cursor.close()

    def create_branslar(self):
        self.cursor = self.mysql.connection.cursor()
        sorgu = '''Create Table If Not Exists branslar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        bransAdi VARCHAR(30) NOT NULL,
        bransAciklama VARCHAR(255)
        )'''
        self.cursor.execute(sorgu)
        self.mysql.connection.commit()
        self.cursor.close()

    def create_gruplar(self):
        self.cursor = self.mysql.connection.cursor()
        sorgu = '''Create Table If Not Exists gruplar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        grupAdi VARCHAR(30) NOT NULL,
        grupBransi VARCHAR(30) NOT NULL,
        grupAciklama VARCHAR(255)
        )'''
        self.cursor.execute(sorgu)
        self.mysql.connection.commit()
        self.cursor.close()

    def create_salonlar(self):
        self.cursor = self.mysql.connection.cursor()
        sorgu = '''Create Table If Not Exists salonlar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        salonAdi VARCHAR(30) NOT NULL,
        salonTipi VARCHAR(30) NOT NULL,
        salonAciklama VARCHAR(255)
        )'''
        self.cursor.execute(sorgu)
        self.mysql.connection.commit()
        self.cursor.close()

    def create_antrenor(self):
        self.cursor = self.mysql.connection.cursor()
        sorgu = '''Create Table If Not Exists antrenor (
        id Int AUTO_INCREMENT PRIMARY KEY,
        antrenorAdSoyad VARCHAR(100) NOT NULL,
        antrenorUserName VARCHAR(20) NOT NULL,
        antrenorPassword VARCHAR(20) NOT NULL
        )'''
        self.cursor.execute(sorgu)
        self.mysql.connection.commit()
        self.cursor.close()
    
    def create_odemeler(self):
        self.cursor = self.mysql.connection.cursor()
        sorgu = ''' Create Table If Not Exists odemeler (
        id Int AUTO_INCREMENT PRIMARY KEY,
        ogrenciId Int NOT NULL,
        ogrenciTC VARCHAR(20),
        ogrenciAdSoyad VARCHAR(100) NOT NULL,
        veliAdSoyad VARCHAR(100),
        veliTelefon VARCHAR(20),
        toplamOdeme DECIMAL(10, 2) NOT NULL,
        toplamOdenen DECIMAL(10, 2),
        odemeTarihleri TEXT,
        odemeMiktarlari TEXT,
        kalanOdeme DECIMAL(10, 2) GENERATED ALWAYS AS (toplamOdeme - toplamOdenen) STORED
        )'''
        self.cursor.execute(sorgu)
        self.mysql.connection.commit()
        self.cursor.close()

 
        
    def update_ogrenciler(self, values):
        self.cursor = self.mysql.connection.cursor()
        sorgu = "Update ogrenciler Set ogrenciTC = %s, ogrenciAd = %s, ogrenciSoyad = %s, ogrenciYasi = %s, ogrenciBrans = %s, ogrenciGrup = %s, veliAdi = %s, veliTelefon = %s, veli2Adi = %s, veli2Telefon = %s, toplamOdeme = %s Where id = %s"
        self.cursor.execute(sorgu, values)
        self.mysql.connection.commit()
        self.cursor.close()

    def search(self, keyword):
        self.cursor = self.mysql.connection.cursor()
        sorgu = "Select * From ogrenciler Where ogrenciAd like '%" + keyword + "%'"
        result = self.cursor.execute(sorgu)
        if result == 0:
            return False
        else:
            values = self.cursor.fetchall()
            return values