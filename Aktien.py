# Stock Master 2026 - WKN Edition
# Lizenz: MIT License
# Urheber: Entwickelt von Gemini AI & [Dein Name/Benutzername]
#
# Hiermit wird unentgeltlich jeder Person das Recht eingeräumt, 
# diese Software zu nutzen, zu kopieren und zu verändern.


import customtkinter as ctk
import yfinance as ticker_data
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
from tkinter import filedialog
import datetime
import smtplib
from email.mime.text import MIMEText

# --- KONFIGURATION ---
try:
    import config
    SMTP_SERVER = getattr(config, 'SMTP_SERVER', "smtp.dein-anbieter.de")
    SMTP_PORT = getattr(config, 'SMTP_PORT', 465)
    EMAIL_USER = getattr(config, 'EMAIL_USER', getattr(config, 'EMAIL_SENDER', "deine-mail@web.de"))
    EMAIL_PW = getattr(config, 'EMAIL_PW', "dein-passwort")
    RECEIVER = getattr(config, 'RECEIVER', "empfaenger@web.de")
except ImportError:
    SMTP_SERVER, SMTP_PORT = "smtp.dein-anbieter.de", 465
    EMAIL_USER, EMAIL_PW, RECEIVER = "deine-mail@web.de", "dein-passwort", "empfaenger@web.de"

class UltimateStockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Stock Master 2026 - Final Edition")
        self.geometry("1400x950")
        ctk.set_appearance_mode("dark")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variablen & Farben
        self.periods = {"1T": "1d", "1W": "5d", "1M": "1mo", "6M": "6mo", "1J": "1y", "5J": "5y"}
        self.current_period = "1mo"
        self.last_ticker = ""
        self.exchanges = {"Xetra": ".DE", "Tradegate": ".TI", "USA": ""}
        self.color_gd10 = "purple"
        self.color_gd200 = "#d35400"

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SEITENLEISTE ---
        self.sidebar = ctk.CTkFrame(self, width=280)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="STOCK MASTER", font=("Impact", 32))
        self.logo_label.pack(pady=(20, 0))
        self.sublogo_label = ctk.CTkLabel(self.sidebar, text="2026 PRO EDITION", font=("Arial", 14, "bold"), text_color="#3498db")
        self.sublogo_label.pack(pady=(0, 20))

        # Eingabe & Button Bereich
        ctk.CTkLabel(self.sidebar, text="Aktien-Eingabe:", font=("Arial", 13, "bold")).pack(pady=(10, 5), padx=20, anchor="w")
        self.entry_symbol = ctk.CTkEntry(self.sidebar, placeholder_text="Symbol (z.B. SAP)")
        self.entry_symbol.pack(pady=5, padx=20, fill="x")
        self.entry_symbol.bind('<Return>', lambda e: self.update_dashboard())

        # DER NEUE ANALYSE BUTTON
        self.btn_analyze = ctk.CTkButton(self.sidebar, text="AKTIE ANALYSIEREN", fg_color="#3498db", hover_color="#2980b9", 
                                         font=("Arial", 13, "bold"), command=self.update_dashboard)
        self.btn_analyze.pack(pady=10, padx=20, fill="x")

        self.exchange_var = ctk.StringVar(value="Xetra")
        ctk.CTkOptionMenu(self.sidebar, values=list(self.exchanges.keys()), variable=self.exchange_var).pack(pady=5, padx=20, fill="x")

        self.chart_type_var = ctk.StringVar(value="Kerzen")
        ctk.CTkOptionMenu(self.sidebar, values=["Linie", "Kerzen"], variable=self.chart_type_var, 
                          command=lambda _: self.update_dashboard(use_last=True)).pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(self.sidebar, text="Optionen:", font=("Arial", 13, "bold")).pack(pady=(20, 5), padx=20, anchor="w")
        self.show_gd10 = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.sidebar, text="GD 10 (Trend)", variable=self.show_gd10, command=lambda: self.update_dashboard(use_last=True)).pack(pady=5, padx=20, anchor="w")
        self.show_gd200 = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.sidebar, text="GD 200 (Invest)", variable=self.show_gd200, command=lambda: self.update_dashboard(use_last=True)).pack(pady=5, padx=20, anchor="w")

        self.send_mail_enabled = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.sidebar, text="E-Mail Signale", variable=self.send_mail_enabled).pack(pady=5, padx=20, anchor="w")

        self.btn_export = ctk.CTkButton(self.sidebar, text="EXCEL EXPORT", fg_color="#27ae60", hover_color="#219150", command=self.export_to_excel)
        self.btn_export.pack(pady=30, padx=20, fill="x")

        self.dedication_label = ctk.CTkLabel(self.sidebar, text="In Zusammenarbeit mit Gemini\nfür Heinz entwickelt. 2026", 
                                             font=("Arial", 10, "italic"), text_color="gray")
        self.dedication_label.pack(side="bottom", pady=20)

        # --- HAUPTBEREICH ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.header_container = ctk.CTkFrame(self.main_content, height=100, fg_color="transparent")
        self.header_container.pack(pady=(0, 10), padx=10, fill="x")
        
        self.title_frame = ctk.CTkFrame(self.header_container, corner_radius=10, fg_color="#2c3e50")
        self.title_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.title_label = ctk.CTkLabel(self.title_frame, text="BÖRSE STARTEN...", font=("Arial", 22, "bold"), text_color="#ecf0f1", anchor="w")
        self.title_label.pack(pady=15, padx=20)

        self.trend_frame = ctk.CTkFrame(self.header_container, corner_radius=10, fg_color=self.color_gd10)
        self.trend_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.trend_label = ctk.CTkLabel(self.trend_frame, text="TREND (GD10)\n--", font=("Arial", 16, "bold"), text_color="white")
        self.trend_label.pack(pady=10)

        self.invest_frame = ctk.CTkFrame(self.header_container, corner_radius=10, fg_color=self.color_gd200)
        self.invest_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        self.invest_label = ctk.CTkLabel(self.invest_frame, text="INVEST (GD200)\n--", font=("Arial", 16, "bold"), text_color="white")
        self.invest_label.pack(pady=10)

        self.chart_frame = ctk.CTkFrame(self.main_content, fg_color="#1e1e1e", corner_radius=15)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.button_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.button_frame.pack(pady=10, padx=20, fill="x")
        for label, p in self.periods.items():
            ctk.CTkButton(self.button_frame, text=label, width=60, height=35, command=lambda code=p: self.change_period(code)).pack(side="left", padx=5, expand=True)

    def format_volume(self, x, pos):
        if x >= 1e6: return f'{x*1e-6:.1f}M'
        if x >= 1e3: return f'{x*1e-3:.0f}K'
        return f'{x:.0f}'

    def calculate_rsi(self, data, window=14):
        if len(data) < window: return pd.Series(50, index=data.index)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def update_dashboard(self, use_last=False):
        if not use_last:
            raw = self.entry_symbol.get().strip().upper()
            if not raw: return
            suffix = self.exchanges[self.exchange_var.get()]
            self.last_ticker = f"{raw}{suffix}" if not raw.endswith(suffix) else raw

        try:
            stock = ticker_data.Ticker(self.last_ticker)
            hist_daily = stock.history(period="2y")
            if hist_daily.empty: 
                self.title_label.configure(text="SYMBOL FEHLER")
                return

            hist_daily['GD10'] = hist_daily['Close'].rolling(10).mean()
            hist_daily['GD200'] = hist_daily['Close'].rolling(200).mean()
            hist_daily['RSI'] = self.calculate_rsi(hist_daily)
            
            latest = hist_daily.iloc[-1]
            price = latest['Close']
            
            name = stock.info.get('longName', self.last_ticker)
            self.title_label.configure(text=f"{name}\n{price:.2f} EUR")

            trend_sig = "KAUFEN" if price > latest['GD10'] else "VERKAUFEN"
            self.trend_label.configure(text=f"TREND (10T)\n{trend_sig}")

            invest_sig = "KAUFEN" if price > latest['GD200'] else "VERKAUFEN"
            self.invest_label.configure(text=f"INVEST (200T)\n{invest_sig}")

            if self.current_period == "1d":
                plot_data = stock.history(period="1d", interval="5m")
                plot_data['GD10'], plot_data['GD200'] = latest['GD10'], latest['GD200']
                plot_data['RSI'] = self.calculate_rsi(plot_data, window=7)
            else:
                days = {"5d":7, "1mo":31, "6mo":183, "1y":366, "5y":1825}.get(self.current_period, 30)
                plot_data = hist_daily.tail(days).copy()

            self._render_chart(plot_data)
        except Exception as e: 
            print(f"Error: {e}")

    def _render_chart(self, data):
        for w in self.chart_frame.winfo_children(): w.destroy()
        plt.close('all')
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1, 1]}, sharex=True)
        fig.patch.set_facecolor('#1e1e1e')
        x_range = range(len(data))

        ax1.set_facecolor('#f5f5f5')
        is_1t = self.current_period == "1d"
        if self.chart_type_var.get() == "Kerzen":
            w = 0.6 if not is_1t else 0.4
            for i in range(len(data)):
                row = data.iloc[i]
                c = '#27ae60' if row['Close'] >= row['Open'] else '#e74c3c'
                ax1.vlines(i, row['Low'], row['High'], color=c, lw=1)
                ax1.add_patch(plt.Rectangle((i-w/2, min(row['Open'], row['Close'])), w, max(abs(row['Open']-row['Close']), 0.001), color=c))
        else:
            ax1.plot(x_range, data['Close'], color='#3498db', lw=2)

        if self.show_gd10.get():
            if is_1t: ax1.axhline(data['GD10'].iloc[0], color=self.color_gd10, ls='--', label="GD10")
            else: ax1.plot(x_range, data['GD10'], color=self.color_gd10, label="GD10", lw=2)
            
        if self.show_gd200.get():
            if is_1t: ax1.axhline(data['GD200'].iloc[0], color=self.color_gd200, ls='--', label="GD200")
            else: ax1.plot(x_range, data['GD200'], color=self.color_gd200, label="GD200", lw=2)

        ax1.set_ylabel("Kurs (EUR)", color="white")
        ax1.legend(loc="upper left", fontsize=8)

        ax2.set_facecolor('#f5f5f5')
        v_colors = ['#27ae60' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#e74c3c' for i in range(len(data))]
        ax2.bar(x_range, data['Volume'], color=v_colors, alpha=0.8)
        ax2.set_ylabel("Volumen", color="white")
        ax2.yaxis.set_major_formatter(FuncFormatter(self.format_volume))

        ax3.set_facecolor('#f5f5f5')
        ax3.plot(x_range, data['RSI'], color='#2980b9', lw=1.5)
        ax3.axhline(70, color='#e74c3c', ls='--', alpha=0.5)
        ax3.axhline(30, color='#27ae60', ls='--', alpha=0.5)
        ax3.set_ylabel("RSI", color="white")
        ax3.set_ylim(0, 100)

        indices = range(0, len(data), max(1, len(data)//8))
        ax3.set_xticks(indices)
        fmt = '%H:%M' if is_1t else '%d.%m'
        ax3.set_xticklabels([data.index[i].strftime(fmt) for i in indices], color='white', fontsize=8)

        for ax in [ax1, ax2, ax3]:
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.1)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def export_to_excel(self):
        if not self.last_ticker: return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                 initialfile=f"Export_{self.last_ticker}")
        if file_path:
            try:
                df = ticker_data.Ticker(self.last_ticker).history(period="2y")
                df.index = df.index.tz_localize(None) 
                df.to_excel(file_path)
            except Exception as e: print(f"Export Error: {e}")

    def change_period(self, p):
        self.current_period = p
        self.update_dashboard(True)

    def on_closing(self):
        plt.close('all')
        self.destroy()

if __name__ == "__main__":
    app = UltimateStockApp()
    app.mainloop()
