"""
Değişiklik Karşılaştırma Modülü (Comparer)
==========================================

Bu modül önceki ve yeni hash'leri karşılaştırır.
Ayrıca önceki kayıtları JSON'da saklar.

Sorumlulukları:
- Hash karşılaştırma
- Önceki hash'i kaydetme/okuma
- Değişiklik tespiti
"""

import json
import os
from typing import Optional
from datetime import datetime


class ContentComparer:
    """
    İçerik değişikliğini tespit eden ve kaydını tutan sınıf.
    
    JSON formatında veri yapısı:
    {
        "url": "https://example.com",
        "last_hash": "abc123...",
        "last_check": "2026-01-04 15:30:00",
        "change_count": 5
    }
    """
    
    def __init__(self, storage_path: str = "storage"):
        """
        Args:
            storage_path: Kayıtların tutulacağı klasör yolu
        """
        self.storage_path = storage_path
        
        # Klasör yoksa oluştur
        os.makedirs(storage_path, exist_ok=True)
    
    def _get_record_file(self, url: str) -> str:
        """
        Her URL için benzersiz dosya adı üretir.
        
        Args:
            url: İzlenen sayfanın URL'i
            
        Returns:
            JSON dosya yolu
            
        Neden URL'i dosya adı yapıyoruz?
        - Her site için ayrı kayıt
        - Kolay erişim
        - Çakışma yok
        
        Problem: URL'de dosya adı için geçersiz karakterler var
        Çözüm: URL'i hash'le → güvenli dosya adı
        """
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.storage_path, f"{url_hash}.json")
    
    def load_previous_hash(self, url: str) -> Optional[str]:
        """
        Bir URL için önceden kaydedilmiş hash'i yükler.
        
        Args:
            url: İzlenen sayfanın URL'i
            
        Returns:
            Önceki hash (varsa)
            None (ilk çalıştırmada)
        """
        record_file = self._get_record_file(url)
        
        # Dosya yoksa → ilk çalıştırma
        if not os.path.exists(record_file):
            return None
        
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('last_hash')
        except Exception as e:
            print(f"[UYARI] Kayit okuma hatasi: {e}")
            return None
    
    def save_hash(self, url: str, new_hash: str) -> None:
        """
        Yeni hash'i kaydeder.
        
        Args:
            url: İzlenen sayfanın URL'i
            new_hash: Yeni hesaplanan hash
        """
        record_file = self._get_record_file(url)
        
        # Önceki kaydı yükle (değişiklik sayısını korumak için)
        old_data = {}
        if os.path.exists(record_file):
            try:
                with open(record_file, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
            except:
                pass
        
        # Yeni veri yapısı
        new_data = {
            'url': url,
            'last_hash': new_hash,
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'change_count': old_data.get('change_count', 0)
        }
        
        # Eğer hash değiştiyse sayacı artır
        if old_data.get('last_hash') and old_data['last_hash'] != new_hash:
            new_data['change_count'] += 1
        
        # Kaydet
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    def has_changed(self, url: str, current_hash: str) -> bool:
        """
        İçeriğin değişip değişmediğini kontrol eder.
        
        Args:
            url: İzlenen sayfanın URL'i
            current_hash: Şu anki hash
            
        Returns:
            True → içerik değişmiş
            False → içerik aynı veya ilk çalıştırma
            
        Önemli: İlk çalıştırmada False döner!
        """
        previous_hash = self.load_previous_hash(url)
        
        # İlk çalıştırma → değişiklik yok sayılır
        if previous_hash is None:
            return False
        
        # Karşılaştır
        return previous_hash != current_hash
    
    def check_and_update(self, url: str, current_hash: str) -> bool:
        """
        Değişikliği kontrol eder ve kaydı günceller.
        
        Args:
            url: İzlenen sayfanın URL'i
            current_hash: Şu anki hash
            
        Returns:
            True → içerik değişmiş
            False → içerik aynı veya ilk çalıştırma
            
        Bu fonksiyon:
        1. Değişikliği kontrol eder
        2. Yeni hash'i kaydeder
        3. Sonucu döndürür
        
        Tek adımda her şeyi yapar → kullanımı kolay
        """
        changed = self.has_changed(url, current_hash)
        
        # Her durumda hash'i güncelle (zaman damgası için)
        self.save_hash(url, current_hash)
        
        return changed


# Test kodu
if __name__ == "__main__":
    from fetcher import ContentFetcher
    from cleaner import HTMLCleaner
    from hasher import ContentHasher
    
    url = "https://kocaeli.tsf.org.tr/egitimler/egitim-programlar"
    
    # Pipeline: Çek → Temizle → Hash'le
    fetcher = ContentFetcher()
    cleaner = HTMLCleaner()
    hasher = ContentHasher()
    comparer = ContentComparer()
    
    print("İçerik çekiliyor...")
    html = fetcher.fetch(url)
    
    if html:
        print("İçerik temizleniyor...")
        clean_text = cleaner.clean(html)
        
        print("Hash oluşturuluyor...")
        current_hash = hasher.generate_hash(clean_text)
        
        print("Değişiklik kontrol ediliyor...")
        changed = comparer.check_and_update(url, current_hash)
        
        print("=" * 60)
        print("SONUÇ")
        print("=" * 60)
        print(f"URL: {url}")
        print(f"Hash: {current_hash}")
        print(f"Değişiklik var mı? {changed}")
        print("=" * 60)
        
        if changed:
            print("[OK] Icerik degismis! Bildirim gonderilmeli.")
        else:
            print("[OK] Icerik ayni veya ilk calistirma.")
