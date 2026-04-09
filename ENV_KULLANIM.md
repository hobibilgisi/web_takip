# .env Dosyası Kullanım Kılavuzu

## Nedir?

`.env` dosyası, uygulamanın hassas bilgilerini (mail adresi, şifre) güvenli bir şekilde saklar.

## Nasıl Çalışır?

### 1. İlk Çalıştırma

Uygulama ilk kez çalıştırıldığında veya "Takibi Başlat" butonuna tıklandığında:

1. `.env` dosyası kontrol edilir
2. Dosya yoksa veya boşsa → **Mail Ayarları Dialog** açılır
3. Kullanıcı bilgileri girer
4. Bilgiler `.env` dosyasına kaydedilir

### 2. Sonraki Çalıştırmalar

- `.env` dosyası otomatik okunur
- Mail bilgileri tekrar sorulmaz
- "⚙️ Mail Ayarlarını Düzenle" butonuyla değiştirilebilir

### 3. Hata Durumunda

Eğer mail gönderme başarısız olursa:

1. Hata mesajı gösterilir
2. Kullanıcı "⚙️ Mail Ayarlarını Düzenle" butonuna tıklayabilir
3. Bilgileri düzeltip kaydedebilir

## .env Dosya Formatı

```env
SENDER_EMAIL=senin@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop
NOTIFY_EMAIL=bildirim@gmail.com
```

## Güvenlik

⚠️ **ÖNEMLİ**: 
- `.env` dosyası GİZLİDİR
- Git'e eklenmez (`.gitignore` ile korunur)
- GitHub'a yüklemeyiniz!
- Şifrenizi kimseyle paylaşmayın

## Manuel Düzenleme

İsterseniz `.env` dosyasını doğrudan düzenleyebilirsiniz:

1. Proje klasöründe `.env` dosyasını açın
2. Değerleri düzenleyin
3. Kaydedin
4. Uygulamayı yeniden başlatın

## Sorun Giderme

### Mail ayarları okunmuyor
- `.env` dosyasının proje kök dizininde olduğundan emin olun
- Dosya formatının doğru olduğunu kontrol edin
- Satır sonlarında boşluk olmamalı

### Şifre çalışmıyor
- Gmail için "Uygulama Şifresi" kullanmalısınız
- Normal Gmail şifreniz ÇALIŞMAZ
- [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) adresinden alın

### Dosya kayboldu
- `.env.example` dosyasını `.env` olarak kopyalayın
- Bilgilerinizi tekrar girin
