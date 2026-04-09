"""
İçerik Çekme Modülü (Fetcher)
=============================

Bu modül web sayfalarından içerik çekme işlemini yapar.
Temiz, güvenli ve hata yönetimi olan bir yapı.
"""

import requests
from typing import Optional


class ContentFetcher:
    """
    Web sayfalarından içerik çeken sınıf.
    
    Sorumlulukları:
    - URL'den HTML içerik çekme
    - Timeout yönetimi
    - HTTP hata yönetimi
    - User-Agent gönderme (bot algılama önleme)
    """
    
    def __init__(self, timeout: int = 10):
        """
        Args:
            timeout: İstek için maksimum bekleme süresi (saniye)
        """
        self.timeout = timeout
        # Bazı siteler bot trafiğini engelliyor, normal tarayıcı gibi görünelim
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch(self, url: str) -> Optional[str]:
        """
        Verilen URL'den HTML içeriği çeker.
        
        Args:
            url: Çekilecek sayfanın tam URL'i
            
        Returns:
            HTML içeriği (başarılıysa)
            None (hata durumunda)
            
        Neden Optional[str]?
        - Ağ hatası olabilir
        - Site erişilemez olabilir
        - Timeout gerçekleşebilir
        Bu yüzden None dönebileceğimizi belirtiyoruz
        """
        try:
            # GET isteği gönder
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # HTTP hata kodlarını kontrol et (404, 500 vs.)
            # raise_for_status() → 4xx veya 5xx varsa exception fırlatır
            response.raise_for_status()
            
            # encoding'i doğru ayarla (Türkçe karakter problemi olmasın)
            response.encoding = response.apparent_encoding
            
            # HTML içeriğini döndür
            return response.text
            
        except requests.exceptions.Timeout:
            # Timeout oldu → site çok yavaş veya erişilemiyor
            print(f"[UYARI] Timeout hatasi: {url} yanit vermedi ({self.timeout}s)")
            return None
            
        except requests.exceptions.ConnectionError:
            # Bağlantı hatası → internet yok veya site down
            print(f"[UYARI] Baglanti hatasi: {url} erisilemez")
            return None
            
        except requests.exceptions.HTTPError as e:
            # HTTP hatası → 404, 500 vs.
            print(f"[UYARI] HTTP hatasi: {e}")
            return None
            
        except Exception as e:
            # Beklenmeyen hata → güvenlik ağı
            print(f"[UYARI] Bilinmeyen hata: {e}")
            return None


# Modül seviyesinde test fonksiyonu
if __name__ == "__main__":
    # Test: Gerçek siteyi çek
    fetcher = ContentFetcher()
    content = fetcher.fetch("https://kocaeli.tsf.org.tr/egitimler/egitim-programlar")
    
    if content:
        print(f"[OK] Icerik basariyla cekildi: {len(content)} karakter")
        print(f"İlk 200 karakter:\n{content[:200]}...")
    else:
        print("[HATA] Icerik cekilemedi")
