"""
Mail Ayarları Dialog Penceresi
==============================

.env dosyası yoksa veya mail gönderme başarısız olursa
kullanıcıdan mail bilgilerini alan pencere.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from dotenv import load_dotenv


class EmailConfigDialog:
    """
    Mail ayarlarını kullanıcıdan alan dialog penceresi.
    
    Bu pencere:
    - .env dosyası yoksa açılır
    - Mail gönderme başarısız olursa açılır
    - Bilgileri .env dosyasına kaydeder
    """
    
    def __init__(self, parent=None, env_path=".env"):
        """
        Args:
            parent: Ana pencere (None olabilir)
            env_path: .env dosya yolu
        """
        self.env_path = env_path
        self.result = None
        
        # Dialog penceresi oluştur
        if parent:
            self.dialog = tk.Toplevel(parent)
        else:
            self.dialog = tk.Tk()
        
        self.dialog.title("Mail Ayarları")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Modal yap (ana pencereyi blokla)
        if parent:
            self.dialog.transient(parent)
            self.dialog.grab_set()
        
        self._create_widgets()
        
        # Pencereyi ortala
        self._center_window()
    
    def _create_widgets(self):
        """Dialog içeriğini oluşturur."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_label = ttk.Label(
            main_frame,
            text="📧 Mail Ayarları",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Açıklama
        info_label = ttk.Label(
            main_frame,
            text="Bildirim göndermek için mail ayarlarınızı girin.\nBu bilgiler güvenli şekilde .env dosyasında saklanır.",
            justify=tk.CENTER
        )
        info_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Gönderen mail
        ttk.Label(
            form_frame,
            text="Gönderen Mail Adresi:",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.sender_entry = ttk.Entry(form_frame, width=50)
        self.sender_entry.grid(row=1, column=0, pady=(0, 15))
        
        # Uygulama şifresi
        ttk.Label(
            form_frame,
            text="Uygulama Şifresi (App Password):",
            font=("Arial", 10, "bold")
        ).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.password_entry = ttk.Entry(form_frame, width=50, show="*")
        self.password_entry.grid(row=3, column=0, pady=(0, 15))
        
        # Bildirim mail
        ttk.Label(
            form_frame,
            text="Bildirim Gönderilecek Mail:",
            font=("Arial", 10, "bold")
        ).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.notify_entry = ttk.Entry(form_frame, width=50)
        self.notify_entry.grid(row=5, column=0, pady=(0, 15))
        
        # Gmail yardım
        help_frame = ttk.Frame(form_frame)
        help_frame.grid(row=6, column=0, sticky=tk.W, pady=(0, 15))
        
        ttk.Label(help_frame, text="ℹ️", foreground="blue").pack(side=tk.LEFT)
        link = ttk.Label(
            help_frame,
            text="Gmail için Uygulama Şifresi Nasıl Alınır?",
            foreground="blue",
            cursor="hand2",
            font=("Arial", 9, "underline")
        )
        link.pack(side=tk.LEFT, padx=(5, 0))
        link.bind("<Button-1>", lambda e: self._open_gmail_help())
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Kaydet",
            command=self._save_settings,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="İptal",
            command=self._cancel,
            width=15
        ).pack(side=tk.LEFT)
        
        # .env'den mevcut değerleri yükle
        self._load_existing_values()
    
    def _load_existing_values(self):
        """Mevcut .env değerlerini form'a yükler."""
        if os.path.exists(self.env_path):
            load_dotenv(self.env_path, override=True)
            
            sender = os.getenv('SENDER_EMAIL', '').strip().strip("'\"")
            password = os.getenv('SENDER_PASSWORD', '').strip().strip("'\"")
            notify = os.getenv('NOTIFY_EMAIL', '').strip().strip("'\"")
            
            if sender:
                self.sender_entry.insert(0, sender)
            if password:
                self.password_entry.insert(0, password)
            if notify:
                self.notify_entry.insert(0, notify)
    
    def _save_settings(self):
        """Ayarları .env dosyasına kaydeder."""
        sender = self.sender_entry.get().strip()
        password = self.password_entry.get().strip()
        notify = self.notify_entry.get().strip()
        
        # Validasyon
        if not sender or '@' not in sender:
            messagebox.showerror("Hata", "Geçerli bir gönderen mail adresi girin")
            return
        
        if not password:
            messagebox.showerror("Hata", "Uygulama şifresi boş olamaz")
            return
        
        if not notify or '@' not in notify:
            messagebox.showerror("Hata", "Geçerli bir bildirim mail adresi girin")
            return
        
        # .env dosyasına kaydet
        try:
            # Değerleri doğrudan yaz (tırnak olmadan)
            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.write("# TSF Takip Sistemi - Mail Ayarları\n")
                f.write("# Bu dosya otomatik oluşturuldu\n\n")
                f.write(f"SENDER_EMAIL={sender}\n")
                f.write(f"SENDER_PASSWORD={password}\n")
                f.write(f"NOTIFY_EMAIL={notify}\n")
            
            self.result = {
                'sender_email': sender,
                'sender_password': password,
                'notify_email': notify
            }
            
            messagebox.showinfo("Başarılı", "Mail ayarları kaydedildi!")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilemedi:\n{e}")
    
    def _cancel(self):
        """Dialog'u iptal eder."""
        self.result = None
        self.dialog.destroy()
    
    def _open_gmail_help(self):
        """Gmail yardım sayfasını açar."""
        import webbrowser
        webbrowser.open("https://myaccount.google.com/apppasswords")
    
    def _center_window(self):
        """Pencereyi ekranın ortasına yerleştirir."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def show(self):
        """
        Dialog'u gösterir ve sonucu bekler.
        
        Returns:
            dict: {'sender_email': ..., 'sender_password': ..., 'notify_email': ...}
            None: İptal edildi
        """
        self.dialog.wait_window()
        return self.result


def load_email_config(env_path=".env"):
    """
    .env dosyasından mail ayarlarını yükler.
    
    Args:
        env_path: .env dosya yolu
        
    Returns:
        dict: Mail ayarları veya None
    """
    if not os.path.exists(env_path):
        return None
    
    # override=True ile mevcut değerleri güncelle
    load_dotenv(env_path, override=True)
    
    sender = os.getenv('SENDER_EMAIL', '').strip().strip("'\"")
    password = os.getenv('SENDER_PASSWORD', '').strip().strip("'\"")
    notify = os.getenv('NOTIFY_EMAIL', '').strip().strip("'\"")
    
    if sender and password and notify:
        return {
            'sender_email': sender,
            'sender_password': password,
            'notify_email': notify
        }
    
    return None


def ensure_email_config(parent=None, env_path=".env"):
    """
    Mail ayarlarını garanti eder. Yoksa kullanıcıdan ister.
    
    Args:
        parent: Ana pencere (opsiyonel)
        env_path: .env dosya yolu
        
    Returns:
        dict: Mail ayarları veya None (kullanıcı iptal etti)
    """
    # Önce mevcut ayarları yükle
    config = load_email_config(env_path)
    
    if config:
        return config
    
    # Yoksa dialog aç
    messagebox.showinfo(
        "Mail Ayarları Gerekli",
        "Bildirim göndermek için mail ayarlarınızı girmeniz gerekiyor."
    )
    
    dialog = EmailConfigDialog(parent, env_path)
    result = dialog.show()
    
    return result


# Test kodu
if __name__ == "__main__":
    # Test 1: Dialog göster
    print("Test: Mail ayarları dialog")
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    
    result = ensure_email_config()
    
    if result:
        print("[OK] Mail ayarlari alindi:")
        print(f"  Gonderen: {result['sender_email']}")
        print(f"  Bildirim: {result['notify_email']}")
    else:
        print("[IPTAL] Kullanici iptal etti")
    
    root.destroy()
