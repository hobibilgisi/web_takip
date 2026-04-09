"""
TSF Web Takip Sistemi
=====================

Web sayfalarındaki değişiklikleri izleyen ve mail ile bildiren sistem.

Kullanım:
    python main.py

Özellikler:
- Belirli URL'leri izleme
- Reklam ve gereksiz içerikleri filtreleme
- Periyodik kontrol (saatlik, günlük vs.)
- Başlangıç ve bitiş tarihi desteği
- Mail bildirimleri
- Kullanıcı dostu arayüz

Gereksinimler:
    pip install requests beautifulsoup4 tkcalendar
"""

import sys
import os

# Windows'ta UTF-8 encoding zorla
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    """Ana program girişi."""
    print("=" * 60)
    print("WEB TAKIP PROGRAMI")
    print("=" * 60)
    print()
    print("Arayuz aciliyor...")
    
    # Uygulamayı başlat
    app = MainWindow()
    app.run()
    
    print("\nUygulama kapatildi.")


if __name__ == "__main__":
    main()
