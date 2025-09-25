# Internationalization (i18n) Implementation für GuideOS Updater

## Implementierte Features

### ✅ Vollständige deutsche Übersetzung
- **GUI-Übersetzung**: Alle Benutzeroberflächen-Texte sind übersetzt
- **Fehlermeldungen**: Authentifizierungs- und Systemdialoge auf Deutsch
- **Benachrichtigungen**: Desktop-Notifications in deutscher Sprache
- **Spaltenüberschriften**: Tabellen-Headers der Update-Liste übersetzt

### ✅ .mo-Datei System
- **Locale-Struktur**: `locale/de/LC_MESSAGES/guideos-updater.mo`
- **Gettext-Integration**: Standard Python gettext für Übersetzungen
- **Automatische Erkennung**: System-Locale wird automatisch erkannt
- **Fallback**: Englisch als Fallback-Sprache bei fehlenden Übersetzungen

### ✅ Desktop-Integration
- **Desktop-Datei**: Deutsche Übersetzungen in .desktop-Datei
- **Keywords**: Deutsche Suchbegriffe hinzugefügt
- **Kategorien**: Systemkategorien für bessere Integration

### ✅ Wartungstools
- **update-translations.sh**: Script zum Aktualisieren der Übersetzungen
- **MANIFEST.in**: Inkludiert Locale-Dateien in Distribution
- **Automatisierung**: Einfache Erweiterung um weitere Sprachen

## Übersetzte Bereiche

### Hauptfenster (main_window.py)
- ✅ Fenstertitel: "GuideOS Updater" / "GuideOS Update-Manager"
- ✅ Spalten: Auswählen, Paket, Aktuelle Version, etc.
- ✅ Buttons: "Alle auswählen", "Updates installieren"
- ✅ Status: "Bereit", "Updates werden installiert..."
- ✅ Dialoge: Bestätigungsdialoge für Installation

### Authentifizierung (auth.py)
- ✅ Dialog-Titel: "Authentifizierung erforderlich"
- ✅ Buttons: "Abbrechen", "Authentifizieren"
- ✅ Beschreibungen: Passwort-Eingabe-Hinweise
- ✅ Warnungen: Feststelltasten-Warnung

### Benachrichtigungen
- ✅ Erfolg: "Updates abgeschlossen"
- ✅ Fehler: "Update fehlgeschlagen"
- ✅ Details: Vollständige Fehlerbeschreibungen

### Update-Statistiken
- ✅ Zähler: "Gesamt: X | APT: Y | Flatpak: Z | Sicherheit: W"
- ✅ Typen: Sicherheits-/Standard-Updates
- ✅ Quellen: APT/Flatpak-Kennzeichnung

## Technische Details

### Gettext-Konfiguration
```python
from utils.i18n import _
text = _("Text to translate")
```

### Locale-Erkennung
- Automatische System-Locale-Erkennung
- Fallback auf Englisch bei unverfügbaren Übersetzungen
- UTF-8 Encoding für deutsche Umlaute

### Build-Integration
- .mo-Dateien werden automatisch in Debian-Pakete eingebunden
- MANIFEST.in inkludiert alle Locale-Dateien
- Setup.py berücksichtigt Übersetzungsdateien

## Verwendung

### Anwendung mit deutscher Locale starten
```bash
# Explizit deutsche Locale setzen
LANGUAGE=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 ./guideos-updater

# Oder mit System-Locale (automatisch)
./guideos-updater
```

### Übersetzungen aktualisieren
```bash
# Script ausführen
./update-translations.sh

# Oder manuell
msgfmt locale/de/LC_MESSAGES/guideos-updater.po -o locale/de/LC_MESSAGES/guideos-updater.mo
```

## Erweiterung um weitere Sprachen

### Neue Sprache hinzufügen (z.B. Französisch)
```bash
# Verzeichnis erstellen
mkdir -p locale/fr/LC_MESSAGES

# .po-Datei kopieren und übersetzen
cp locale/de/LC_MESSAGES/guideos-updater.po locale/fr/LC_MESSAGES/
# Französische Übersetzungen eintragen

# Kompilieren
msgfmt locale/fr/LC_MESSAGES/guideos-updater.po -o locale/fr/LC_MESSAGES/guideos-updater.mo
```

### .desktop-Datei erweitern
```ini
Name[fr]=GuideOS Updater
Comment[fr]=Gestionnaire de mise à jour pour les paquets APT et Flatpak
```

Die Internationalisierung ist vollständig implementiert und einsatzbereit!