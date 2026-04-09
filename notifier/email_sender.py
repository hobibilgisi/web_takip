"""
E-posta Bildirimi Modülü (Email Sender)
========================================

Bu modül SMTP ile e-posta bildirimleri gönderir.
Gmail, Outlook, Yandex gibi servislerle çalışır.

UYARI: Bu modül gerçek mail göndermeden ÖNCE kullanıcıdan:
- Mail adresi
- Uygulama şifresi (App Password)
talep eder.
"""

import smtplib
from email.message import EmailMessage
from typing import Optional
from dataclasses import dataclass


@dataclass
class EmailConfig:
    """
    Mail gönderme için gerekli ayarlar.
    
    Attributes:
        sender_email: Gönderen mail adresi (örn: senin@gmail.com)
        sender_password: Uygulama şifresi (NOT: Normal şifre değil!)
        smtp_server: SMTP sunucu adresi (örn: smtp.gmail.com)
        smtp_port: SMTP portu (genelde 465 veya 587)
    """
    sender_email: str
    sender_password: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 465


class EmailSender:
    """
    E-posta gönderme işlemlerini yöneten sınıf.
    
    Desteklenen servisler:
    - Gmail (smtp.gmail.com:465)
    - Outlook (smtp-mail.outlook.com:587)
    - Yahoo (smtp.mail.yahoo.com:465)
    - Yandex (smtp.yandex.com.tr:465)
    
    Güvenlik notu:
    - Gmail için "Uygulama Şifresi" (App Password) gerekir
    - Normal şifre ÇALIŞMAZ!
    - 2 faktörlü doğrulama açık olmalı
    """
    
    def __init__(self, config: EmailConfig):
        """
        Args:
            config: Mail ayarları
        """
        self.config = config
        self.last_error = None  # Son hata mesajı
    
    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        E-posta gönderir.
        
        Args:
            to_email: Alıcı mail adresi
            subject: Mail konusu
            body: Mail içeriği
            html: True ise HTML mail, False ise düz metin
            
        Returns:
            True → başarılı
            False → hata
        """
        try:
            # E-posta mesajı oluştur
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = self.config.sender_email
            msg['To'] = to_email
            
            # İçeriği ayarla
            if html:
                msg.set_content(body, subtype='html')
            else:
                msg.set_content(body)
            
            # SMTP bağlantısı kur ve gönder
            # SSL kullanıyoruz → güvenli
            with smtplib.SMTP_SSL(
                self.config.smtp_server,
                self.config.smtp_port
            ) as smtp:
                # Giriş yap
                smtp.login(
                    self.config.sender_email,
                    self.config.sender_password
                )
                
                # Mail gönder
                smtp.send_message(msg)
            
            print(f"[OK] Mail gonderildi: {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print("[HATA] Mail gonderme hatasi: Kimlik dogrulama basarisiz")
            print("   -> Gmail kullaniyorsaniz 'Uygulama Sifresi' gerekir")
            print("   -> https://myaccount.google.com/apppasswords")
            print(f"   -> Hata detayi: {e}")
            # Hata detayını döndür (UI'da kullanılabilir)
            self.last_error = f"Kimlik doğrulama hatası: {e}"
            return False
            
        except smtplib.SMTPException as e:
            error_msg = f"Mail gonderme hatasi: {e}"
            print(f"[HATA] {error_msg}")
            self.last_error = error_msg
            return False
            
        except Exception as e:
            error_msg = f"Beklenmeyen hata: {e}"
            print(f"[HATA] {error_msg}")
            self.last_error = error_msg
            return False
    
    def send_change_notification(
        self,
        to_email: str,
        url: str,
        change_details: Optional[str] = None
    ) -> bool:
        """
        İçerik değişikliği bildirimi gönderir.
        
        Args:
            to_email: Alıcı
            url: Değişen sayfanın URL'i
            change_details: Opsiyonel detay bilgisi
            
        Returns:
            Başarı durumu
        """
        subject = "[DEGISIKLIK] Icerik Degisikligi Tespit Edildi"
        
        body = f"""
Merhaba,

Izlediginiz web sayfasinda degisiklik tespit edildi:

URL: {url}
Tarih: {self._get_current_time()}

{change_details or 'Icerik degisti.'}

Bu otomatik bir bildirimdir.

---
Web Takip Programi
"""
        
        return self.send(to_email, subject, body)
    
    def send_tracking_start(
        self, 
        to_email: str, 
        url: str,
        interval_text: str = "Belirtilmemiş",
        end_date_text: str = "Sonsuz"
    ) -> bool:
        """
        Takip başlangıç bildirimi.
        
        Args:
            to_email: Alıcı
            url: İzlenen URL
            interval_text: Kontrol sıklığı (örn: "Saatlik", "Günlük")
            end_date_text: Bitiş tarihi metni veya "Sonsuz"
        """
        subject = "[BASLADI] Takip Baslatildi"
        
        body = f"""
Merhaba,

Web sayfasi takibi basariyla baslatildi:

URL: {url}
Baslangic Tarihi: {self._get_current_time()}
Kontrol Sikligi: {interval_text}
Bitis Tarihi: {end_date_text}

Degisiklikler tespit edildiginde bu adrese bildirim gonderilecektir.

---
Web Takip Programi
"""
        
        return self.send(to_email, subject, body)
    
    def send_tracking_end(
        self, 
        to_email: str, 
        url: str,
        check_count: int = 0,
        change_count: int = 0
    ) -> bool:
        """
        Takip bitiş bildirimi.
        
        Args:
            to_email: Alıcı
            url: İzlenen URL
            check_count: Toplam kontrol sayısı
            change_count: Toplam değişiklik sayısı
        """
        subject = "[BITTI] Takip Sonlandirildi"
        
        body = f"""
Merhaba,

Web sayfasi takibi sona erdi:

URL: {url}
Bitis: {self._get_current_time()}
Toplam Kontrol: {check_count}
Tespit Edilen Degisiklik: {change_count}

Belirlediginiz takip suresi tamamlandi.

---
Web Takip Programi
"""
        
        return self.send(to_email, subject, body)
    
    @staticmethod
    def _get_current_time() -> str:
        """Şu anki zamanı formatlanmış olarak döndürür."""
        from datetime import datetime
        return datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    
    @staticmethod
    def get_smtp_config_for_provider(email: str) -> tuple[str, int]:
        """
        Mail adresine göre otomatik SMTP ayarları döndürür.
        
        Args:
            email: Kullanıcının mail adresi
            
        Returns:
            (smtp_server, smtp_port)
            
        Desteklenen servisler:
        - Gmail, Google Apps
        - Outlook, Hotmail, Live
        - Yahoo
        - Yandex
        """
        email_lower = email.lower()
        
        if 'gmail' in email_lower or 'googlemail' in email_lower:
            return ('smtp.gmail.com', 465)
        
        elif 'outlook' in email_lower or 'hotmail' in email_lower or 'live' in email_lower:
            return ('smtp-mail.outlook.com', 587)
        
        elif 'yahoo' in email_lower:
            return ('smtp.mail.yahoo.com', 465)
        
        elif 'yandex' in email_lower:
            return ('smtp.yandex.com.tr', 465)
        
        else:
            # Varsayılan (Gmail)
            return ('smtp.gmail.com', 465)


# Test kodu
if __name__ == "__main__":
    print("=" * 60)
    print("E-POSTA GONDERIMI TEST MODU")
    print("=" * 60)
    print()
    print("Bu test senin mail bilgilerinle calisir.")
    print("UYARI: Gmail kullaniyorsan 'Uygulama Sifresi' gerekir!")
    print()
    
    # Kullanıcıdan bilgi al
    sender = input("Gönderen mail adresin: ").strip()
    password = input("Uygulama şifresi (görünmez): ").strip()
    receiver = input("Test maili gönderilecek adres: ").strip()
    
    if not all([sender, password, receiver]):
        print("[HATA] Eksik bilgi! Test iptal edildi.")
    else:
        # SMTP ayarlarını otomatik belirle
        smtp_server, smtp_port = EmailSender.get_smtp_config_for_provider(sender)
        
        # Config oluştur
        config = EmailConfig(
            sender_email=sender,
            sender_password=password,
            smtp_server=smtp_server,
            smtp_port=smtp_port
        )
        
        # EmailSender oluştur
        email_sender = EmailSender(config)
        
        # Test maili gönder
        print(f"\nMail gonderiliyor ({smtp_server})...")
        success = email_sender.send(
            to_email=receiver,
            subject="Test - TSF Takip Sistemi",
            body="Bu bir test mailidir. Eger bunu okuyorsan, sistem calisiyor!"
        )
        
        if success:
            print("\n[OK] Test basarili! Mail kutunu kontrol et.")
        else:
            print("\n[HATA] Test basarisiz. Ayarlari kontrol et.")
