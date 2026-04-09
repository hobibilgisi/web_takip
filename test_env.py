"""
.env Test Script
================
Mail ayarlarının doğru okunduğunu test eder.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.email_config_dialog import load_email_config

print("=" * 60)
print(".ENV DOSYASI TEST")
print("=" * 60)
print()

# .env dosyasını oku
config = load_email_config()

if config:
    print("[OK] Mail ayarlari basariyla okundu:")
    print(f"  Gonderen: {config['sender_email']}")
    print(f"  Sifre: {config['sender_password'][:4]}****")
    print(f"  Bildirim: {config['notify_email']}")
    print()
    print("[OK] Ayarlar gecerli!")
else:
    print("[HATA] Mail ayarlari okunamadi!")
    print("  .env dosyasi yok veya bos")

print()
print("=" * 60)
