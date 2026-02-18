Stock Master 2026 - Final Edition
Ein leichtgewichtiges Analyse-Tool für Aktien, speziell optimiert für den deutschen Markt (Ticker-Support) und Linux-Systeme.

Features
Ticker Support: Ticker Eingabe und ergänzt Börsenplatz-Suffixe.
Börsenplatz-Wahl: Unterstützung für XETRA, Tradegate und Frankfurt.
Interaktive Charts: Schnelle Zeitraumanpassung (1T bis MAX) mit Visualisierung durch Matplotlib.
Excel-Export: Speichert historische Kurse des letzten Jahres direkt in eine .xlsx Datei.
Email Benachrichtigung: Benachrichtig bei kauf oder verkaufsignale der 10 oder 200 Tageschart
Linux Optimized: Clean Shutdown Logik und volle Unterstützung für CustomTkinter unter Linux Mint 22.3.
Installation
Repository klonen oder .py Datei speichern.
Abhängigkeiten installieren: pip install customtkinter yfinance pandas matplotlib openpyxl
Programm starten: python3 stock_master.py
Hinweise zur Installation unter Linux Mint 22.3
Wenn du dein Analyse-Programm später unter Linux Mint startest, achte darauf, dass du immer zuerst die venv-Umgebung im Python Projekt/Programm-Ordner aktivierst (source venv/bin/activate), bevor du dein Skript ausführst.

Da du unter Linux arbeitest, kannst du dein Skript jetzt noch „veredeln“. Wenn du im Terminal in deinem Projekt/Programmordner folgendes eingibst, Es machst die Datei ausführbar:

Terminal/Bash

chmod +x deine_datei.py Und wenn du ganz oben in die erste Zeile deines Codes (über die Imports) diesen sogenannten „Shebang“ setzt:

Python #!/usr/bin/env python3 ...dann kannst du das Programm in Mint sogar per Doppelklick starten, fast wie eine installierte App.

Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert - frei für alle! Entwickelt von Gemini AI & dem Linux-Nutzer, Heinz Hochhalter.
