"""
Ana Arayüz Penceresi (Main Window)
===================================

Tkinter ile web izleme arayüzü.

Bileşenler:
- URL girişi
- Periyot seçimi
- Başlangıç/Bitiş tarihi seçimi
- Mail adresi girişi
- Mail şifresi girişi
- Başlat/Durdur butonları
- Durum göstergesi
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry  # pip install tkcalendar
import threading
import os
from dotenv import load_dotenv
from ui.email_config_dialog import EmailConfigDialog, ensure_email_config


class MainWindow:
    """
    Ana uygulama penceresi.
    
    Sorumlulukları:
    - Kullanıcıdan ayarları almak
    - Takibi başlatmak/durdurmak
    - Durum bilgilerini göstermek
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Web Takip Programi")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        self.root.minsize(800, 600)
        
        # Modern tema renkleri
        self.colors = {
            'bg': '#f5f5f5',
            'primary': '#2196F3',
            'secondary': '#1976D2',
            'success': '#4CAF50',
            'danger': '#f44336',
            'text': '#212121',
            'text_light': '#757575'
        }
        
        # Arka planda çalışan task runner
        self.task_runner = None
        
        # UI bileşenlerini oluştur
        self._create_widgets()
        
        # Pencere kapatma olayını yakala
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        """Tüm UI bileşenlerini oluşturur."""
        
        # Grid weight ayarları (pencere büyüdükçe içerik de büyüsün)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Ana container (padding için)
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Main frame grid weight ayarları
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Başlık
        title_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=60)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        title_frame.grid_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🌐 Web Takip Programi",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors['primary'],
            fg='white'
        )
        title_label.pack(expand=True)
        
        # ----- URL Girişi -----
        row = 1
        ttk.Label(main_frame, text="Takip Edilecek URL:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.url_entry = ttk.Entry(main_frame, font=("Segoe UI", 10))
        self.url_entry.grid(row=row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # ----- Periyot Seçimi -----
        row += 2
        ttk.Label(main_frame, text="Kontrol Periyodu:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.period_combo = ttk.Combobox(
            main_frame,
            values=["5 Dakikada Bir", "Saatlik", "6 Saatte Bir", "Günlük", "Haftalık", "Aylık"],
            state="readonly",
            width=20
        )
        self.period_combo.grid(row=row+1, column=0, sticky=tk.W, pady=(0, 15))
        
        # ----- Tarih Aralığı -----
        row += 2
        ttk.Label(main_frame, text="Takip Süresi:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        
        # Başlangıç tarihi
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=row+1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(date_frame, text="Başlangıç:").grid(row=0, column=0, padx=(0, 10))
        self.start_date = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy'
        )
        self.start_date.grid(row=0, column=1, padx=(0, 20))
        
        # Başlangıç saati
        ttk.Label(date_frame, text="Saat:").grid(row=0, column=2, padx=(0, 5))
        self.start_hour = ttk.Spinbox(date_frame, from_=0, to=23, width=5, format="%02.0f")
        self.start_hour.set(datetime.now().hour)
        self.start_hour.grid(row=0, column=3, padx=(0, 5))
        
        ttk.Label(date_frame, text=":").grid(row=0, column=4)
        self.start_minute = ttk.Spinbox(date_frame, from_=0, to=59, width=5, format="%02.0f")
        self.start_minute.set(datetime.now().minute)
        self.start_minute.grid(row=0, column=5)
        
        # Bitiş tarihi
        end_date_frame = ttk.Frame(main_frame)
        end_date_frame.grid(row=row+2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        self.infinite_var = tk.BooleanVar(value=True)
        self.infinite_check = ttk.Checkbutton(
            end_date_frame,
            text="Sonsuz takip",
            variable=self.infinite_var,
            command=self._toggle_end_date
        )
        self.infinite_check.grid(row=0, column=0, padx=(0, 20))
        
        ttk.Label(end_date_frame, text="Bitiş:").grid(row=0, column=1, padx=(0, 10))
        self.end_date = DateEntry(
            end_date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            state='disabled'
        )
        self.end_date.set_date(datetime.now() + timedelta(days=7))
        self.end_date.grid(row=0, column=2, padx=(0, 20))
        
        # Bitiş saati
        ttk.Label(end_date_frame, text="Saat:").grid(row=0, column=3, padx=(0, 5))
        self.end_hour = ttk.Spinbox(end_date_frame, from_=0, to=23, width=5, format="%02.0f", state='disabled')
        self.end_hour.set(23)
        self.end_hour.grid(row=0, column=4, padx=(0, 5))
        
        ttk.Label(end_date_frame, text=":").grid(row=0, column=5)
        self.end_minute = ttk.Spinbox(end_date_frame, from_=0, to=59, width=5, format="%02.0f", state='disabled')
        self.end_minute.set(59)
        self.end_minute.grid(row=0, column=6)
        
        # ----- Mail Ayarları -----
        row += 3
        mail_frame = ttk.Frame(main_frame)
        mail_frame.grid(row=row, column=0, columnspan=2, pady=(10, 15))
        
        ttk.Label(
            mail_frame,
            text="Mail Ayarları (.env dosyasından okunur)",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            mail_frame,
            text="⚙️ Mail Ayarlarını Düzenle",
            command=self._open_email_settings,
            width=25
        ).pack(side=tk.LEFT)
        
        # ----- Butonlar -----
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(10, 10))
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ Takibi Baslat",
            command=self._start_tracking,
            width=22,
            height=2,
            bg=self.colors['success'],
            fg='white',
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Takibi Durdur",
            command=self._stop_tracking,
            state=tk.DISABLED,
            width=22,
            height=2,
            bg=self.colors['danger'],
            fg='white',
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            cursor='hand2',
            disabledforeground='#999999'
        )
        self.stop_button.grid(row=0, column=1)
        
        # ----- Durum Göstergesi -----
        row += 1
        status_frame = ttk.LabelFrame(main_frame, text="📊 Durum Logları", padding="10")
        status_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        main_frame.rowconfigure(row, weight=1)
        
        # Scrollbar ekle
        status_scroll = ttk.Scrollbar(status_frame)
        status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.status_text = tk.Text(
            status_frame,
            height=15,
            state=tk.DISABLED,
            bg="#ffffff",
            fg=self.colors['text'],
            font=("Consolas", 10),
            wrap=tk.WORD,
            yscrollcommand=status_scroll.set,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['text_light']
        )
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scroll.config(command=self.status_text.yview)
        
        # İlk durum mesajı
        self._log_status("[SISTEM] Hazir. Ayarlari yapin ve takibi baslatin.")
    
    def _toggle_end_date(self):
        """Sonsuz takip checkbox'ı değiştiğinde çağrılır."""
        if self.infinite_var.get():
            self.end_date.configure(state=tk.DISABLED)
            self.end_hour.configure(state=tk.DISABLED)
            self.end_minute.configure(state=tk.DISABLED)
        else:
            self.end_date.configure(state=tk.NORMAL)
            self.end_hour.configure(state="readonly")
            self.end_minute.configure(state="readonly")
    
    def _open_email_settings(self):
        """Mail ayarları dialog'unu açar."""
        dialog = EmailConfigDialog(self.root)
        result = dialog.show()
        
        if result:
            self._log_status("[OK] Mail ayarları güncellendi")
    
    def _log_status(self, message: str):
        """Durum penceresine mesaj ekler."""
        self.status_text.configure(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state=tk.DISABLED)
    
    def _validate_inputs(self) -> bool:
        """Kullanıcı girişlerini doğrular."""
        # URL kontrolü
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Hata", "URL girmelisiniz")
            return False
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Hata", "Gecerli bir URL girin (http:// veya https:// ile baslamali)")
            return False
        
        # Periyot kontrolü
        if not self.period_combo.get():
            messagebox.showerror("Hata", "Kontrol periyodu secmelisiniz")
            return False
        
        # Mail ayarlarını kontrol et
        email_config = ensure_email_config(self.root)
        if not email_config:
            messagebox.showerror("Hata", "Mail ayarlari girilmedi. Takip baslatilamaz.")
            return False
        
        return True
    
    def _start_tracking(self):
        """Takibi başlatır."""
        if not self._validate_inputs():
            return
        
        try:
            # Ayarları al
            from scheduler.task_runner import WatchConfig, TaskRunner, IntervalConverter
            from notifier.email_sender import EmailSender, EmailConfig
            
            # Tarihleri oluştur
            start_date = datetime.combine(
                self.start_date.get_date(),
                datetime.min.time()
            ).replace(
                hour=int(self.start_hour.get()),
                minute=int(self.start_minute.get())
            )
            
            # Başlangıç tarihi geçmişte ise şu ana ayarla
            now = datetime.now()
            if start_date < now:
                start_date = now
                self._log_status("[UYARI] Baslangic tarihi gecmiste, su ana ayarlandi")
            
            if self.infinite_var.get():
                end_date = None
            else:
                end_date = datetime.combine(
                    self.end_date.get_date(),
                    datetime.min.time()
                ).replace(
                    hour=int(self.end_hour.get()),
                    minute=int(self.end_minute.get())
                )
                
                # Bitiş başlangıçtan önce olamaz
                if end_date <= start_date:
                    messagebox.showerror("Hata", "Bitis tarihi baslangic tarihinden sonra olmali")
                    return
            
            # Email config - .env'den oku
            from ui.email_config_dialog import load_email_config
            email_data = load_email_config()
            
            if not email_data:
                # .env yoksa veya boşsa kullanıcıdan iste
                email_data = ensure_email_config(self.root)
                if not email_data:
                    messagebox.showerror("Hata", "Mail ayarlari gerekli")
                    return
            
            sender = email_data['sender_email']
            password = email_data['sender_password']
            notify_email = email_data['notify_email']
            
            smtp_server, smtp_port = EmailSender.get_smtp_config_for_provider(sender)
            email_config = EmailConfig(sender, password, smtp_server, smtp_port)
            email_sender = EmailSender(email_config)
            
            # Watch config
            watch_config = WatchConfig(
                url=self.url_entry.get().strip(),
                start_date=start_date,
                end_date=end_date,
                interval_seconds=IntervalConverter.get_seconds(self.period_combo.get()),
                notify_email=notify_email
            )
            
            # Task runner oluştur ve başlat
            self.task_runner = TaskRunner(
                watch_config,
                email_sender,
                self._status_callback
            )
            
            if self.task_runner.start():
                self._log_status("[OK] Takip baslatildi (arka planda calisiyor)")
                self._log_status(f"  Baslangic: {start_date.strftime('%d.%m.%Y %H:%M')}")
                if end_date:
                    self._log_status(f"  Bitis: {end_date.strftime('%d.%m.%Y %H:%M')}")
                else:
                    self._log_status(f"  Bitis: Sonsuz")
                self._log_status(f"  Periyot: {self.period_combo.get()}")
                
                # Buton durumlarını güncelle
                self.start_button.configure(state=tk.DISABLED)
                self.stop_button.configure(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Takip baslatilamadi:\n{e}")
            self._log_status(f"[HATA] {e}")
    
    def _stop_tracking(self):
        """Takibi durdurur."""
        if self.task_runner:
            self.task_runner.stop()
            self._log_status("[DURDURULDU] Takip manuel olarak durduruldu")
            
            # Buton durumlarını güncelle
            self.start_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
    
    def _status_callback(self, status: dict):
        """Task runner'dan gelen durum güncellemelerini işler."""
        # Thread-safe UI güncellemesi
        self.root.after(0, self._update_ui_status, status)
    
    def _update_ui_status(self, status: dict):
        """UI'daki durum bilgilerini günceller."""
        if status['last_check_time']:
            time_str = status['last_check_time'].strftime('%H:%M:%S')
            self._log_status(
                f"[DURUM] Kontrol: {status['check_count']}, "
                f"Degisiklik: {status['change_count']}, "
                f"Son: {time_str}"
            )
        
        if status['last_error']:
            self._log_status(f"[UYARI] Hata: {status['last_error']}")
        
        # Takip bittiyse butonları güncelle
        if status['has_finished']:
            self.start_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
    
    def _on_closing(self):
        """Pencere kapatıldığında çağrılır."""
        if self.task_runner and self.task_runner.state.is_running:
            if messagebox.askokcancel("Çıkış", "Takip devam ediyor. Yine de çıkmak istiyor musunuz?"):
                self.task_runner.stop()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Uygulamayı başlatır."""
        self.root.mainloop()


# Ana program
if __name__ == "__main__":
    app = MainWindow()
    app.run()
