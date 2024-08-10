from wtforms import Form, SelectField, StringField, DateField, IntegerField, TextAreaField, DecimalField, SubmitField, validators, PasswordField, EmailField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm


class RegisterForm(FlaskForm):
    adSoyad = StringField("* Adınız Soyadınız", validators=[validators.DataRequired()])
    telefon = StringField("* Telefon numaranızı başında 0 ile birlikte 11 haneli olarak giriniz", validators=[validators.DataRequired(), validators.length(min=11, max=11, message="Telefon numaranız 11 haneli olmalıdır."), validators.Regexp(r'^\d+$', message="Telefon numaranız sadece rakamlardan oluşmalıdır")])
    ePosta = EmailField("* E-Posta adresiniz", validators=[validators.DataRequired(), validators.Email()])
    userName = StringField("Kullanıcı adınız 'isteğe bağlı'")
    password = PasswordField("* Şifreniz", validators=[validators.DataRequired()])
    kulupAdi = StringField("* Kulüp-kurum adınız", validators=[validators.DataRequired()])


class LoginForm(FlaskForm):
    userName = StringField("* Kullanıcı adı veya E-Posta", validators=[validators.DataRequired()])
    password = PasswordField("* Şifreniz", validators=[validators.DataRequired()])


class OgrenciForm(FlaskForm):
    ogrenciFoto = FileField("Öğrenci Fotoğrafı", name="ogrenciFoto", validators=[FileAllowed(['jpg', 'png', 'jpeg'], "Sadece jpg, png ve jpeg dosyalarına izin verilir")])
    ogrenciTC = StringField("Öğrencinin TC Kimlik Numarası", validators=[validators.length(max=11)])
    ogrenciAd = StringField("* Öğrencinin Adı", validators=[validators.length(max=50), validators.DataRequired()])
    ogrenciSoyad = StringField("* Öğrencinin Soyadı", validators=[validators.length(max=50), validators.DataRequired()])
    ogrenciTelefon = StringField("Öğrencinin Telefonu", validators=[validators.length(max=50)])
    ogrenciYas = IntegerField("Öğrencinin Yaşı", validators=[validators.NumberRange(min=1, message="Yaş değeri pozitif bir sayı olmalıdır.")])
    ogrenciDogumTarihi = DateField("Öğrencinin Doğum Tarihi", format = '%Y-%m-%d')
    ogrenciBrans = SelectField("Branşı", choices=[])
    ogrenciGrup = SelectField("Grubu", choices=[])
    veliAd = StringField("* Velinin Adı Soyadı", validators=[validators.length(max=50), validators.DataRequired()])
    veliTelefon = StringField("* Velinin Telefon Numarası", validators=[validators.length(max=50), validators.DataRequired()])
    veli2Ad = StringField("İkinci Veli Adı Soyadı", validators=[validators.length(max=50)])
    veli2Telefon = StringField("İkinci Velinin Telefon Numarası", validators=[validators.length(max=50)])
    ilkOdemeTarihi =DateField("* İlk ödeme tarihi belirleyin", format='%Y-%m-%d', validators=[validators.DataRequired()])
    toplamOdeme = DecimalField("* Toplam Ödeme Miktarı", validators=[validators.DataRequired(), validators.NumberRange(min=0, message="Ödeme miktarı 0 dan küçük olamaz")])

    def fill_form(self, sozluk):
        self.ogrenciFoto.data = sozluk['ogrenciFoto']
        self.ogrenciTC.data = sozluk['ogrenciTC']
        self.ogrenciAd.data = sozluk['ogrenciAd']
        self.ogrenciSoyad.data = sozluk['ogrenciSoyad']
        self.ogrenciTelefon.data = sozluk['ogrenciTelefon']
        self.ogrenciYas.data = sozluk['ogrenciYas']
        self.ogrenciDogumTarihi.data = sozluk['ogrenciDogumTarihi']
        self.ogrenciBrans.data = sozluk['ogrenciBrans']
        self.ogrenciGrup.data = sozluk['ogrenciGrup']
        self.veliAd.data = sozluk['veliAd']
        self.veliTelefon.data = sozluk['veliTelefon']
        self.veli2Ad.data = sozluk['veli2Ad']
        self.veli2Telefon.data = sozluk['veli2Telefon']
        self.ilkOdemeTarihi.data = sozluk["ilkOdemeTarihi"]
        self.toplamOdeme.data = sozluk['toplamOdeme']


class OdemeForm(FlaskForm):
    odemeMiktari = DecimalField("* Yapılan ödeme miktarı", validators=[validators.NumberRange(min=0, message="Ödeme miktarı minumum 0 olabilir"), validators.DataRequired()])
    odemeTarihi = DateField("Bir sonraki ödeme tarihi", format='%Y-%m-%d')
    odemeyiYapan = StringField("Ödemeyi yapan")
    
    def fill_form(self, time):
        self.odemeTarihi.data = time
