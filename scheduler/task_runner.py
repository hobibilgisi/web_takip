"""
Zamanlama ve Takip Yöneticisi (Task Runner)
===========================================

Bu modül:
- Arka planda (thread ile) çalışır
- Başlangıç/bitiş tarihlerini kontrol eder
- Periyodik olarak içerik kontrolü yapar
- Bildirimleri yönetir

KRİTİK: Bu modül arayüzü dondurmaz!
"""

import threading
import time
from datetime import datetime
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class WatchConfig:
    """
    Takip konfigürasyonu.
    
    Attributes:
        url: İzlenecek URL
        start_date: Takip başlangıç tarihi
        end_date: Takip bitiş tarihi (None = sonsuz)
        interval_seconds: Kontrol periyodu (saniye)
        notify_email: Bildirim gönderilecek mail
        target_selector: İzlenecek CSS selector (None = tüm sayfa)
    """
    url: str
    start_date: datetime
    end_date: Optional[datetime]
    interval_seconds: int
    notify_email: str
    target_selector: Optional[str] = None


class WatchState:
    """
    Takip durumu yönetimi.
    
    Bu sınıf thread-safe olmalı çünkü:
    - Arka plan thread'i okur/yazar
    - UI thread'i okur/yazar
    """
    
    def __init__(self):
        self.is_running = False           # Thread çalışıyor mu?
        self.has_started = False          # Takip başladı mı?
        self.has_finished = False         # Takip bitti mi?
        self.last_check_time = None       # Son kontrol zamanı
        self.check_count = 0              # Toplam kontrol sayısı
        self.change_count = 0             # Toplam değişiklik sayısı
        self.last_error = None            # Son hata mesajı
        
        # Thread güvenliği için kilit
        self._lock = threading.Lock()
    
    def update_status(self, **kwargs):
        """Thread-safe durum güncelleme."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def get_status(self) -> dict:
        """Thread-safe durum okuma."""
        with self._lock:
            return {
                'is_running': self.is_running,
                'has_started': self.has_started,
                'has_finished': self.has_finished,
                'last_check_time': self.last_check_time,
                'check_count': self.check_count,
                'change_count': self.change_count,
                'last_error': self.last_error
            }


class TaskRunner:
    """
    Takip görevini yöneten ana sınıf.
    
    Sorumlulukları:
    - Thread yönetimi
    - Tarih kontrolü
    - İçerik kontrolü
    - Bildirim yönetimi
    """
    
    def __init__(
        self,
        config: WatchConfig,
        email_sender,  # EmailSender instance
        status_callback: Optional[Callable] = None
    ):
        """
        Args:
            config: Takip ayarları
            email_sender: Mail gönderen nesne
            status_callback: Durum güncellemesi için callback (UI için)
        """
        self.config = config
        self.email_sender = email_sender
        self.status_callback = status_callback
        
        self.state = WatchState()
        self.thread: Optional[threading.Thread] = None
    
    def start(self) -> bool:
        """
        Takibi başlatır.
        
        Returns:
            True → başarıyla başladı
            False → zaten çalışıyor veya hata
        """
        if self.state.is_running:
            print("[UYARI] Takip zaten calisiyor")
            return False
        
        # Thread oluştur ve başlat
        self.thread = threading.Thread(
            target=self._watch_loop,
            daemon=True  # Ana program kapandığında thread de kapansın
        )
        
        self.state.update_status(is_running=True)
        self.thread.start()
        
        print("[OK] Takip baslatildi (arka planda calisiyor)")
        return True
    
    def stop(self) -> bool:
        """
        Takibi durdurur.
        
        Returns:
            True → başarıyla durduruldu
            False → zaten durmuş
        """
        if not self.state.is_running:
            print("[UYARI] Takip zaten durmus")
            return False
        
        self.state.update_status(is_running=False)
        
        # Thread'in durmasını bekle (maksimum 5 saniye)
        if self.thread:
            self.thread.join(timeout=5)
        
        print("[OK] Takip durduruldu")
        return True
    
    def _watch_loop(self):
        """
        Ana takip döngüsü (thread içinde çalışır).
        
        Akış:
        1. Tarih kontrolü
        2. Başlangıç bildirimi (ilk defa)
        3. İçerik kontrolü (aktif dönemde)
        4. Bitiş bildirimi (bitiş zamanında)
        5. Bekleme
        """
        print("[TAKIP] Dongu basladi")
        
        while self.state.is_running:
            try:
                now = datetime.now()
                
                # AŞAMA 1: Başlangıç kontrolü
                if now >= self.config.start_date and not self.state.has_started:
                    self._handle_start()
                
                # AŞAMA 2: Bitiş kontrolü
                if self.config.end_date and now > self.config.end_date:
                    self._handle_end()
                    break  # Döngüden çık
                
                # AŞAMA 3: İçerik kontrolü (aktif dönemde)
                if self.state.has_started and not self.state.has_finished:
                    self._check_content()
                
                # AŞAMA 4: Callback çağır (UI güncellemesi için)
                if self.status_callback:
                    self.status_callback(self.state.get_status())
                
                # AŞAMA 5: Bekle
                time.sleep(self.config.interval_seconds)
                
            except Exception as e:
                error_msg = f"Dongu hatasi: {e}"
                print(f"[HATA] {error_msg}")
                self.state.update_status(last_error=error_msg)
                
                # Hata durumunda kısa bekle ve devam et
                time.sleep(10)
        
        print("[TAKIP] Dongu sona erdi")
    
    def _handle_start(self):
        """Takip başlangıcını işler."""
        print("\n" + "=" * 60)
        print("[TAKIP BAŞLADI]")
        print("=" * 60)
        
        # Bayrağı kaldır
        self.state.update_status(has_started=True)
        
        # Periyot metnini oluştur
        interval_text = IntervalConverter.get_interval_text(self.config.interval_seconds)
        
        # Bitiş tarihi metnini oluştur
        if self.config.end_date:
            end_date_text = self.config.end_date.strftime('%d.%m.%Y %H:%M')
        else:
            end_date_text = "Sonsuz"
        
        # Mail gönder
        success = self.email_sender.send_tracking_start(
            self.config.notify_email,
            self.config.url,
            interval_text=interval_text,
            end_date_text=end_date_text
        )
        
        if success:
            print("[OK] Baslangic bildirimi gonderildi")
        else:
            error_msg = f"Baslangic bildirimi gonderilemedi: {getattr(self.email_sender, 'last_error', 'Bilinmeyen hata')}"
            print(f"[HATA] {error_msg}")
            self.state.update_status(last_error=error_msg)
    
    def _handle_end(self):
        """Takip bitişini işler."""
        print("\n" + "=" * 60)
        print("[TAKIP BITTI]")
        print("=" * 60)
        
        # İstatistikleri al
        status = self.state.get_status()
        check_count = status.get('check_count', 0)
        change_count = status.get('change_count', 0)
        
        # Bayrağı kaldır
        self.state.update_status(
            has_finished=True,
            is_running=False
        )
        
        # Mail gönder (istatistiklerle birlikte)
        success = self.email_sender.send_tracking_end(
            self.config.notify_email,
            self.config.url,
            check_count=check_count,
            change_count=change_count
        )
        
        if success:
            print("[OK] Bitis bildirimi gonderildi")
        else:
            error_msg = f"Bitis bildirimi gonderilemedi: {getattr(self.email_sender, 'last_error', 'Bilinmeyen hata')}"
            print(f"[HATA] {error_msg}")
            self.state.update_status(last_error=error_msg)
    
    def _check_content(self):
        """İçerik değişikliğini kontrol eder."""
        from core.fetcher import ContentFetcher
        from core.cleaner import HTMLCleaner
        from core.hasher import ContentHasher
        from core.comparer import ContentComparer
        
        print(f"\n[KONTROL] Icerik kontrol ediliyor... ({datetime.now().strftime('%H:%M:%S')})")
        
        try:
            # Pipeline: Çek → Temizle → Hash → Karşılaştır
            fetcher = ContentFetcher()
            cleaner = HTMLCleaner(target_selector=self.config.target_selector)
            hasher = ContentHasher()
            comparer = ContentComparer()
            
            # 1. Çek
            html = fetcher.fetch(self.config.url)
            if not html:
                raise Exception("İçerik çekilemedi")
            
            # 2. Temizle
            clean_text = cleaner.clean(html)
            
            # 3. Hash
            current_hash = hasher.generate_hash(clean_text)
            
            # 4. Karşılaştır
            has_changed = comparer.check_and_update(self.config.url, current_hash)
            
            # 5. Güncelle
            self.state.update_status(
                last_check_time=datetime.now(),
                check_count=self.state.check_count + 1
            )
            
            # 6. Değişiklik varsa bildir
            if has_changed:
                print("[DEGISIKLIK] Icerik degisti!")
                
                self.state.update_status(
                    change_count=self.state.change_count + 1
                )
                
                # Mail gönder
                success = self.email_sender.send_change_notification(
                    self.config.notify_email,
                    self.config.url
                )
                
                if success:
                    print("[OK] Degisiklik bildirimi gonderildi")
                else:
                    error_msg = f"Degisiklik bildirimi gonderilemedi: {getattr(self.email_sender, 'last_error', 'Bilinmeyen hata')}"
                    print(f"[HATA] {error_msg}")
                    self.state.update_status(last_error=error_msg)
            else:
                print("[OK] Icerik ayni")
            
        except Exception as e:
            error_msg = f"Icerik kontrolu hatasi: {e}"
            print(f"[HATA] {error_msg}")
            self.state.update_status(last_error=error_msg)


# Periyot dönüşüm fonksiyonları
class IntervalConverter:
    """Kullanıcı dostu periyotları saniyeye çevirir."""
    
    FIVE_MINUTES = 300
    HOUR = 3600
    SIX_HOURS = 21600
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000  # 30 gün kabul ediliyor
    
    @staticmethod
    def get_seconds(period: str) -> int:
        """
        Periyot string'ini saniyeye çevirir.
        
        Args:
            period: "Saatlik", "Günlük" vs.
            
        Returns:
            Saniye cinsinden değer
        """
        period_map = {
            "5 Dakikada Bir": IntervalConverter.FIVE_MINUTES,
            "Saatlik": IntervalConverter.HOUR,
            "6 Saatte Bir": IntervalConverter.SIX_HOURS,
            "Günlük": IntervalConverter.DAY,
            "Haftalık": IntervalConverter.WEEK,
            "Aylık": IntervalConverter.MONTH
        }
        
        return period_map.get(period, IntervalConverter.HOUR)
    
    @staticmethod
    def get_interval_text(seconds: int) -> str:
        """
        Saniyeyi kullanıcı dostu metne çevirir.
        
        Args:
            seconds: Saniye cinsinden periyot
            
        Returns:
            Kullanıcı dostu metin (örn: "Saatlik", "Günlük")
        """
        seconds_map = {
            IntervalConverter.FIVE_MINUTES: "5 Dakikada Bir",
            IntervalConverter.HOUR: "Saatlik",
            IntervalConverter.SIX_HOURS: "6 Saatte Bir",
            IntervalConverter.DAY: "Günlük",
            IntervalConverter.WEEK: "Haftalık",
            IntervalConverter.MONTH: "Aylık"
        }
        
        # Tam eşleşme varsa döndür
        if seconds in seconds_map:
            return seconds_map[seconds]
        
        # Yoksa hesapla
        if seconds < 3600:
            return f"{seconds // 60} Dakikada Bir"
        elif seconds < 86400:
            return f"{seconds // 3600} Saatte Bir"
        elif seconds < 604800:
            return f"{seconds // 86400} Günde Bir"
        else:
            return f"{seconds // 604800} Haftada Bir"


# Test kodu
if __name__ == "__main__":
    from datetime import timedelta
    from notifier.email_sender import EmailSender, EmailConfig
    
    print("=" * 60)
    print("ZAMANLAMALI TAKIP TEST MODU")
    print("=" * 60)
    print()
    print("Bu test 1 dakika sonra baslayacak ve 3 dakika surecek.")
    print("Her 30 saniyede bir kontrol yapilacak.")
    print()
    
    # Mail ayarları (test için)
    sender = input("Gönderen mail: ").strip()
    password = input("Uygulama şifresi: ").strip()
    receiver = input("Alıcı mail: ").strip()
    
    if not all([sender, password, receiver]):
        print("[HATA] Eksik bilgi!")
    else:
        # Email sender oluştur
        smtp_server, smtp_port = EmailSender.get_smtp_config_for_provider(sender)
        email_config = EmailConfig(sender, password, smtp_server, smtp_port)
        email_sender = EmailSender(email_config)
        
        # Watch config oluştur
        now = datetime.now()
        watch_config = WatchConfig(
            url="https://kocaeli.tsf.org.tr/egitimler/egitim-programlar",
            start_date=now + timedelta(minutes=1),  # 1 dakika sonra başla
            end_date=now + timedelta(minutes=4),    # 4 dakika sonra bitir
            interval_seconds=30,                    # 30 saniyede bir kontrol
            notify_email=receiver
        )
        
        # Status callback (test için basit print)
        def status_update(status):
            print(f"[DURUM] Kontrol={status['check_count']}, Degisiklik={status['change_count']}")
        
        # Task runner oluştur ve başlat
        runner = TaskRunner(watch_config, email_sender, status_update)
        runner.start()
        
        print(f"\n[ZAMAN] Baslangic: {watch_config.start_date.strftime('%H:%M:%S')}")
        print(f"[ZAMAN] Bitis: {watch_config.end_date.strftime('%H:%M:%S')}")
        print("\nBekliyor... (Ctrl+C ile durdurmak icin)")
        
        try:
            # Ana thread'i beklet
            while runner.state.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[DURDURULDU] Kullanici tarafindan durduruldu")
            runner.stop()
        
        print("\nTest tamamlandi.")
