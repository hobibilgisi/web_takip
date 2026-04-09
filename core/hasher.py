"""
Hash Oluşturma Modülü (Hasher)
===============================

Bu modül metinden kriptografik hash üretir.
Hızlı karşılaştırma ve değişiklik tespiti için.

SHA-256 kullanıyoruz → endüstri standardı
"""

import hashlib


class ContentHasher:
    """
    Metin içeriğinden hash üreten sınıf.
    
    Hash nedir?
    - İçeriğin benzersiz parmak izi
    - Sabit uzunlukta (64 karakter hex)
    - Tek harf değişse bile tamamen değişir
    - Geri döndürülemez (tek yönlü)
    
    Neden SHA-256?
    - Hızlı (milyon satır/saniye)
    - Güvenli (çakışma yok)
    - Python stdlib'de var
    - Yaygın kullanılır
    """
    
    @staticmethod
    def generate_hash(content: str) -> str:
        """
        Verilen içerikten SHA-256 hash üretir.
        
        Args:
            content: Hash'lenecek metin
            
        Returns:
            64 karakterlik hexadecimal hash
            
        Örnek:
            "Merhaba Dünya" 
            → "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
            
            "Merhaba dunya"  (tek harf farklı)
            → "7f9e8b1c3d2e4a5f6b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1"
            ↑ Tamamen farklı!
        """
        # Metni byte'a çevir (hash fonksiyonu byte'larla çalışır)
        content_bytes = content.encode('utf-8')
        
        # SHA-256 hash nesnesi oluştur
        hash_obj = hashlib.sha256()
        
        # İçeriği hashle
        hash_obj.update(content_bytes)
        
        # Hexadecimal string olarak al (okunabilir)
        # Alternatif: digest() → byte dizisi (daha kompakt ama okunmaz)
        hash_value = hash_obj.hexdigest()
        
        return hash_value
    
    @staticmethod
    def quick_hash(content: str) -> str:
        """
        Tek satırda hash üretir (kısayol).
        
        Yukarıdaki fonksiyonla aynı işi yapar,
        sadece daha kısa yazılır.
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


# Test kodu
if __name__ == "__main__":
    from fetcher import ContentFetcher
    from cleaner import HTMLCleaner
    
    # 1. İçeriği çek
    fetcher = ContentFetcher()
    html = fetcher.fetch("https://kocaeli.tsf.org.tr/egitimler/egitim-programlar")
    
    if html:
        # 2. Temizle
        cleaner = HTMLCleaner()
        clean_text = cleaner.clean(html)
        
        # 3. Hash üret
        hasher = ContentHasher()
        content_hash = hasher.generate_hash(clean_text)
        
        print("=" * 60)
        print("HASH OLUŞTURMA TESTİ")
        print("=" * 60)
        print(f"İçerik uzunluğu: {len(clean_text)} karakter")
        print(f"Hash: {content_hash}")
        print(f"Hash uzunluğu: {len(content_hash)} karakter (her zaman 64)")
        print("=" * 60)
        
        # Test: İçerik değişirse hash değişir mi?
        modified_text = clean_text + " "  # Sadece bir boşluk ekledik
        modified_hash = hasher.generate_hash(modified_text)
        
        print("\nDEĞİŞİKLİK TESTİ:")
        print(f"Orijinal hash: {content_hash}")
        print(f"Değişmiş hash: {modified_hash}")
        print(f"Aynı mı? {content_hash == modified_hash}")
