# Problem Çözümü: Mail Ayarları Tekrar İsteniyor

## Problem
Kullanıcı mail ayarlarını dialog'a girip "Kaydet" butonuna basıyor, "Kaydedildi" mesajını alıyor ama "Takibi Başlat" butonuna bastığında tekrar mail ayarları soruluyor.

## Neden Oldu?
1. `set_key()` fonksiyonu .env dosyasına değerleri **tek tırnak içinde** yazıyordu:
   ```env
   SENDER_EMAIL='satranckupu@gmail.com'
   ```

2. `load_dotenv()` bu değerleri okurken bazen tırnakları kaldıramıyordu

3. `load_email_config()` fonksiyonu yalnızca boşlukları temizliyordu (`.strip()`), tırnakları değil

## Çözüm

### 1. .env Dosya Formatını Düzelttik
**Önceki format** (yanlış):
```env
SENDER_EMAIL='satranckupu@gmail.com'
SENDER_PASSWORD='vdbi scis ppbo ntsj'
```

**Yeni format** (doğru):
```env
SENDER_EMAIL=satranckupu@gmail.com
SENDER_PASSWORD=vdbi scis ppbo ntsj
```

### 2. Kaydetme Mantığını Değiştirdik
**Önceki kod**:
```python
set_key(self.env_path, 'SENDER_EMAIL', sender)
```
→ Bu otomatik olarak tek tırnak ekliyordu

**Yeni kod**:
```python
with open(self.env_path, 'w', encoding='utf-8') as f:
    f.write(f"SENDER_EMAIL={sender}\n")
    f.write(f"SENDER_PASSWORD={password}\n")
    f.write(f"NOTIFY_EMAIL={notify}\n")
```
→ Doğrudan yazıyoruz, tırnak yok

### 3. Okuma Mantığını İyileştirdik
**Önceki kod**:
```python
sender = os.getenv('SENDER_EMAIL', '').strip()
```
→ Sadece boşluk temizliyor

**Yeni kod**:
```python
sender = os.getenv('SENDER_EMAIL', '').strip().strip("'\"")
```
→ Hem boşluk hem de tek/çift tırnak temizliyor

### 4. override=True Ekledik
```python
load_dotenv(env_path, override=True)
```
→ Mevcut environment değişkenlerini günceller (cache problemi çözülür)

## Değişen Dosyalar

1. ✅ `.env` - Tırnaklar kaldırıldı
2. ✅ `ui/email_config_dialog.py` - Kaydetme ve okuma mantığı düzeltildi
3. ✅ `test_env.py` - Test scripti eklendi

## Test Adımları

1. **Mevcut .env dosyasını kontrol et**:
   ```bash
   cat .env
   ```
   Tırnak olmamalı!

2. **Test scriptini çalıştır**:
   ```bash
   python test_env.py
   ```
   "✓ Mail ayarları başarıyla okundu" görmeli

3. **Uygulamayı başlat**:
   ```bash
   python main.py
   ```

4. **"Takibi Başlat" butonuna tıkla**:
   - Mail dialog AÇILMAMALI
   - Direkt takip başlamalı

## Artık Nasıl Çalışıyor?

### İlk Çalıştırma (`.env` yok):
1. Uygulama açılır
2. "Takibi Başlat" → Dialog açılır
3. Mail bilgilerini gir → Kaydet
4. `.env` dosyasına **tırnaksız** yazılır
5. Takip başlar ✅

### Sonraki Çalıştırmalar (`.env` var):
1. Uygulama açılır
2. `.env` otomatik okunur
3. "Takibi Başlat" → Dialog AÇILMAZ
4. Takip direkt başlar ✅

### Ayar Değiştirme:
1. "⚙️ Mail Ayarlarını Düzenle" butonuna tıkla
2. Bilgileri güncelle
3. Kaydet
4. `.env` yeniden yazılır (yine **tırnaksız**)

## Kritik Değişiklikler

### `email_config_dialog.py` - `_save_settings()`:
```python
# ÖNCEDEN:
set_key(self.env_path, 'SENDER_EMAIL', sender)  # Tırnak ekler

# ŞİMDİ:
with open(self.env_path, 'w') as f:
    f.write(f"SENDER_EMAIL={sender}\n")  # Tırnak yok
```

### `email_config_dialog.py` - `load_email_config()`:
```python
# ÖNCEDEN:
sender = os.getenv('SENDER_EMAIL', '').strip()  # Sadece boşluk

# ŞİMDİ:
sender = os.getenv('SENDER_EMAIL', '').strip().strip("'\"")  # Tırnak da temizle
load_dotenv(env_path, override=True)  # Cache güncelle
```

## Sonuç
✅ Problem çözüldü!
✅ Mail ayarları artık doğru kaydediliyor
✅ Tekrar sorulmuyor
✅ .env formatı düzgün

## Ekstra: Hata Durumunda
Eğer hala problem varsa:

1. `.env` dosyasını tamamen sil
2. Uygulamayı yeniden başlat
3. Dialog açılacak
4. Bilgileri tekrar gir
5. Artık doğru formatta kaydedilecek
