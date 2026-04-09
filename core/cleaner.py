"""
HTML Temizleme Modülü (Cleaner)
================================

Bu modül ham HTML'i temizleyip, yalnızca anlamlı içeriği çıkarır.
Reklamları, scriptleri, gereksiz boşlukları ayıklar.

BU MODÜL YANLANCA ALARM ORANINI BELİRLER!
"""

from bs4 import BeautifulSoup
from typing import Optional, List


class HTMLCleaner:
    """
    HTML içeriğini temizleyen ve normalize eden sınıf.
    
    Sorumlulukları:
    - Script/style etiketlerini kaldırma
    - Reklam alanlarını tespit edip çıkarma
    - Boşlukları normalize etme
    - İsteğe bağlı DOM seçimi (belirli bir alanı izleme)
    """
    
    # Reklam olma ihtimali yüksek CSS class/id anahtar kelimeleri
    # Gerçek hayatta kanıtlanmış liste
    AD_KEYWORDS = [
        'ad', 'ads', 'advert', 'advertisement', 'banner',
        'sponsor', 'promo', 'promotion', 'commercial',
        'google-ad', 'adsense', 'adsbygoogle',
        'sidebar-ad', 'top-banner', 'bottom-banner'
    ]
    
    # Reklam taşıyan HTML etiketleri
    AD_TAGS = ['iframe', 'ins']  # ins → Google AdSense
    
    def __init__(self, target_selector: Optional[str] = None):
        """
        Args:
            target_selector: İzlenecek alan (CSS selector)
                             None → tüm sayfa izlenir
                             ".content" → sadece content alanı izlenir
        
        Örnek selectors:
        - ".egitim-listesi"  → sadece eğitim listesi
        - "#main-content"    → id ile seçim
        - "div.content"      → etiket + class
        """
        self.target_selector = target_selector
    
    def clean(self, html: str) -> str:
        """
        HTML'i temizleyip normalize eder.
        
        Args:
            html: Ham HTML içeriği
            
        Returns:
            Temizlenmiş metin içeriği
            
        İşlem sırası (önemli):
        1. HTML parse et
        2. Hedef alanı seç (varsa)
        3. Scriptleri sil
        4. Reklamları sil
        5. Metne çevir
        6. Normalize et
        """
        # BeautifulSoup ile parse et
        # html.parser → Python'la gelir, hızlıdır
        soup = BeautifulSoup(html, 'html.parser')
        
        # AŞAMA 1: Hedef alan seçimi (DOM bazlı izleme)
        if self.target_selector:
            # Sadece belirtilen alanı al
            target = soup.select_one(self.target_selector)
            if target:
                soup = target  # Artık sadece bu alanla çalış
            else:
                # Selector bulunamadı → uyarı ver ama devam et
                print(f"[UYARI] Selector '{self.target_selector}' bulunamadi, tum sayfa kullaniliyor")
        
        # AŞAMA 2: Script ve Style etiketlerini tamamen kaldır
        # Bunlar görsel içerik ama bizim için gürültü
        for tag in soup(['script', 'style']):
            tag.decompose()  # decompose → tamamen sil (extract değil)
        
        # AŞAMA 3: Reklam alanlarını kaldır
        self._remove_ads(soup)
        
        # AŞAMA 4: Metne çevir
        # separator=" " → etiketler arasına boşluk koy
        # strip=True → satır başı/sonu boşluklarını temizle
        text = soup.get_text(separator=' ', strip=True)
        
        # AŞAMA 5: Normalize et (çok önemli)
        text = self._normalize_text(text)
        
        return text
    
    def _remove_ads(self, soup: BeautifulSoup) -> None:
        """
        Reklam olabilecek elementleri DOM'dan siler.
        
        Args:
            soup: BeautifulSoup nesnesi (in-place değiştirilir)
        
        Strateji:
        1. İframe'leri sil (çoğu reklamdır)
        2. 'ins' etiketlerini sil (Google AdSense)
        3. Class/ID'sinde reklam kelimesi olanları sil
        """
        # Reklam etiketlerini sil
        for tag_name in self.AD_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        # Class veya ID'sinde reklam kelimesi olanları bul
        for keyword in self.AD_KEYWORDS:
            # Class ile arama
            # class_=lambda x: x and keyword in x.lower()
            # → class varsa ve içinde keyword geçiyorsa
            for tag in soup.find_all(class_=lambda x: x and keyword in str(x).lower()):
                tag.decompose()
            
            # ID ile arama
            for tag in soup.find_all(id=lambda x: x and keyword in str(x).lower()):
                tag.decompose()
    
    def _normalize_text(self, text: str) -> str:
        """
        Metni normalize eder.
        
        Args:
            text: Ham metin
            
        Returns:
            Normalize edilmiş metin
            
        Neden gerekli?
        - "Merhaba    Dünya" vs "Merhaba Dünya" → aynı içerik
        - Satır sonları vs boşluklar → gürültü
        - Büyük/küçük harf → genelde önemli değil ama şimdilik koruyalım
        """
        # Tüm boşluk karakterlerini split et
        # ['Merhaba', 'Dünya'] gibi listeye çevir
        words = text.split()
        
        # Tek boşlukla birleştir
        normalized = ' '.join(words)
        
        # Küçük harfe çevir (isteğe bağlı, tartışmalı)
        # Eğer "Eğitim" vs "eğitim" farkını görmek istemezsen aç
        # normalized = normalized.lower()
        
        return normalized


# Test kodu
if __name__ == "__main__":
    from fetcher import ContentFetcher
    
    # 1. İçeriği çek
    fetcher = ContentFetcher()
    html = fetcher.fetch("https://kocaeli.tsf.org.tr/egitimler/egitim-programlar")
    
    if html:
        # 2. Tüm sayfayı temizle
        cleaner = HTMLCleaner()
        clean_text = cleaner.clean(html)
        
        print("=" * 60)
        print("TÜM SAYFA TEMİZLENMİŞ HALİ")
        print("=" * 60)
        print(f"Karakter sayısı: {len(clean_text)}")
        print(f"İlk 500 karakter:\n{clean_text[:500]}")
        print("=" * 60)
        
        # 3. Belirli bir alanı temizle (örnek)
        # NOT: Gerçek selector'ı siteden inspect ederek bulacağız
        # cleaner_targeted = HTMLCleaner(target_selector=".content")
        # targeted_text = cleaner_targeted.clean(html)
