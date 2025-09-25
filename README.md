# GuideOS Updater - GuideOS Update Manager

Ein GUI Update Manager für APT und Flatpak Pakete, ähnlich wie mintupdate aus Linux Mint.

## Features

- **APT Package Updates**: Automatische Erkennung und Installation von APT-Paketen
- **Flatpak Application Updates**: Unterstützung für Flatpak-Anwendungen  
- **Security Updates**: Spezielle Kennzeichnung von Sicherheitsupdates
- **Modern GTK3 Interface**: Benutzerfreundliche Oberfläche
- **Update-Auswahl**: Selektive Installation von Updates
- **Progress Tracking**: Fortschrittsanzeige während der Installation
- **Logging**: Detaillierte Protokollierung aller Aktionen

## Systemanforderungen

- Linux-System mit APT (Debian/Ubuntu-basiert)
- Python 3.6+
- GTK 3
- Optional: Flatpak für Flatpak-Support

## Installation

### System-Abhängigkeiten installieren

```bash
# Auf Ubuntu/Debian:
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-notify-0.7 python3-apt flatpak apt-utils
```

### Anwendung ausführen

```bash
# Direkter Start:
python3 main.py

# Oder über das bereitgestellte Script:
chmod +x guideos-updater
./guideos-updater
```

## Installation und Setup

### Schnell-Setup:
```bash
# 1. Setup ausführen (empfohlen mit sudo für PolicyKit)
sudo python3 setup.py

# 2. Anwendung starten
./gup
```

### Manuelle Installation der Abhängigkeiten:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-notify-0.7 python3-apt flatpak apt-utils policykit-1
```

## Verwendung

1. **Starten**: Führen Sie `./guideos-updater` aus
2. **Updates werden automatisch gesucht** beim Start
3. **Alle Updates sind standardmäßig ausgewählt**
4. **Installieren**: Klicken Sie "Install Updates" - PolicyKit fragt nach Berechtigung
5. **Nach erfolgreicher Installation wird die Liste automatisch aktualisiert**

## Projekt-Struktur

```
guideos-updater/
├── main.py                 # Haupt-Einstiegspunkt
├── guideos-updater         # Executable Script
├── core/                   # Kern-Funktionalität
│   ├── update_manager.py   # Zentrale Update-Verwaltung
│   ├── apt_manager.py      # APT Package Manager
│   └── flatpak_manager.py  # Flatpak Manager
├── gui/                    # GUI-Komponenten
│   └── main_window.py      # Haupt-Fenster
├── utils/                  # Hilfsprogramme
│   └── logger.py           # Logging-System
└── README.md               # Diese Datei
```

## Authentifizierung

### PolicyKit (empfohlen):
- **Automatische Berechtigung** für `apt update` ohne Passwort-Eingabe
- **GUI-Passwort-Dialog** für Paket-Installation
- **Sicher**: Nutzt das System-PolicyKit-Framework

### Sudo-Fallback:
- Falls PolicyKit nicht verfügbar ist
- Grafischer Passwort-Dialog für alle Operationen
- **Niemals als root starten** - die Anwendung fragt nach Berechtigung

## Neue Features

- ✅ **PolicyKit Integration**: Elegante Rechteverwaltung ohne ständige Passwort-Abfragen
- ✅ **Auto-Selektion**: Alle Updates standardmäßig ausgewählt
- ✅ **Auto-Refresh**: Liste wird nach erfolgreicher Installation automatisch aktualisiert
- ✅ **Desktop-Integration**: .desktop-Datei wird automatisch erstellt

## Entwicklung

Das Projekt ist modular aufgebaut:

- **UpdateManager**: Zentrale Koordination aller Update-Quellen
- **APTManager**: Behandlung von APT/Debian-Paketen
- **FlatpakManager**: Behandlung von Flatpak-Anwendungen
- **MainWindow**: GTK3-basierte Benutzeroberfläche
- **Logger**: Einheitliches Logging-System

## Beiträge

Dieses Projekt ist inspiriert von Linux Mint's mintupdate. Beiträge und Verbesserungsvorschläge sind willkommen.

## Lizenz

Dieses Projekt steht unter einer Open-Source-Lizenz. Details siehe LICENSE-Datei.