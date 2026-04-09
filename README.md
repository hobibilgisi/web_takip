# Web Takip Sistemi

Web sayfalarındaki değişiklikleri takip eden ve mail ile bildiren Python uygulaması.

## Özellikler

- ✅ Belirli URL'leri periyodik olarak izleme
- ✅ HTML içerikten reklam ve gereksiz bölümleri filtreleme
- ✅ Hash tabanlı akıllı değişiklik tespiti
- ✅ Başlangıç ve bitiş tarihi desteği
- ✅ E-posta bildirimleri (başlangıç, değişiklik, bitiş)
- ✅ Kullanıcı dostu Tkinter arayüzü
- ✅ Arka planda thread ile çalışma

## Kurulum

1. Gerekli paketleri kurun:
```bash
pip install requests beautifulsoup4 tkcalendar python-dotenv
```

Veya:
```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:
```bash
python main.py
```

3. **İlk Çalıştırma**: Uygulama otomatik olarak mail ayarları için bir dialog açacaktır.

## Kullanım

### Takip Ayarları

1. **URL Girişi**: İzlemek istediğiniz web sayfasının tam URL'ini girin
2. **Periyot Seçimi**: Ne sıklıkla kontrol yapılacağını seçin (Saatlik, Günlük vs.)
3. **Tarih Aralığı**: Takibin ne zaman başlayıp biteceğini belirleyin
4. **Mail Ayarlarını Düzenle**: Gerekirse "⚙️ Mail Ayarlarını Düzenle" butonuna tıklayarak ayarları değiştirin
5. **Başlat**: "▶ yarlar `.env` dosyasına kaydedilir (bir daha sorulmaz)

### Takip Ayarları

1. **URL Girişi**: İzlemek istediğiniz web sayfasının tam URL'ini girin
2. **Periyot Seçimi**: Ne sıklıkla kontrol yapılacağını seçin (Saatlik, Günlük vs.)
3. **Tarih Aralığı**: Takibin ne zaman başlayıp biteceğini belirleyin
4. **Mail Ayarları**: 
   - Gönderen mail adresinizi girin
   - Gmail için "Uygulama Şifresi" oluşturun ([Buradan](https://myaccount.google.com/apppasswords))
   - Bildirimlerin gönderileceği mail adresini girin
5. **Başlat**: "Takibi Başlat" butonuna tıklayın

## Gmail İçin Uygulama Şifresi Nasıl Alınır?

1. Google hesabınıza girin
2. [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) adresine gidin
3. "Uygulama şifresi oluştur" seçeneğine tıklayın
4. Oluşturulan 16 haneli şifreyi kopyalayın
5. Bu şifreyi arayüzdeki "Uygulama Şifresi" alanına yapıştırın

## Proje Yapısı

```
web_takip/
├── main.py                 # Ana program girişi
├── ├── main_window.py     # Tkinter arayüz
│   └── email_config_dialog.py  # Mail ayarları dialog
├── storage/               # Veri kayıtları (otomatik oluşur)
├── .env                   # Mail ayarları (GİZLİ - git'e eklenmez)
└── .env.example           # Örnek .env dosyası
│   ├── cleaner.py         # HTML temizleme
│   ├── hasher.py          # Hash üretme
│   └── comparer.py        # Değişiklik tespiti
├── notifier/              # Bildirim sistemi
│   └── email_sender.py    # Mail gönderme
├── scheduler/             # Zamanlama
- **Güvenlik**: Mail bilgileri `.env` dosyasında (git'e eklenmez)
│   └── task_runner.py     # Arka plan takip
├── ui/                    # Kullanıcı arayüzü
│   └── main_window.py     # Tkinter arayüz
└── storage/               # Veri kayıtları (otomatik oluşur)
```

## Teknik Detaylar

- **Python 3.12+**
- **Threading**: Arayüzü dondurmadan arka planda çalışır
- **Hash Algoritması**: SHA-256 ile içerik karşılaştırma
- **SMTP**: SSL ile güvenli mail gönderimi
- **Veri Formatı**: JSON tabanlı kayıt sistemi

## Desteklenen Mail Servisleri

- Gmail
- Outlook / Hotmail
- Yahoo Mail
- Yandex Mail

## Lisans

Kişisel kullanım için serbesttir.
