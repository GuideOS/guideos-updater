#!/usr/bin/env python3
"""
Demo für PolicyKit-Verhalten in GUP
Diese Version zeigt, wann und warum PolicyKit-Dialoge erscheinen
"""

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def show_policykit_info():
    """Erkläre das PolicyKit-Verhalten"""
    print("=" * 60)
    print("GUP Update Manager - PolicyKit Information")
    print("=" * 60)
    print()
    print("📋 WANN ERSCHEINEN PASSWORT-DIALOGE:")
    print()
    print("1. 🔍 BEIM ERSTEN START:")
    print("   - Für 'apt update' (Cache-Aktualisierung)")
    print("   - Normalerweise EINMALIG pro Session")
    print()
    print("2. 🔧 BEIM INSTALLIEREN:")
    print("   - Für 'apt install' (Paket-Installation)")
    print("   - Pro Installation oder Batch")
    print()
    print("🎯 DAS IST NORMAL UND ERWÜNSCHT!")
    print("   PolicyKit sorgt für sichere Rechteverwaltung")
    print("   ohne dauerhaft erhöhte Rechte.")
    print()
    print("⚙️  KONFIGURATION:")
    print("   Bearbeiten Sie config.py um zu ändern:")
    print("   - POLICYKIT_FOR_CACHE_UPDATE = False  # Kein Dialog für Cache")
    print("   - POLICYKIT_FOR_INSTALL = True       # Dialog für Installation")
    print()
    print("🚀 STARTEN SIE JETZT DIE DEMO:")
    print("   - Das folgende Passwort-Fenster ist PolicyKit")
    print("   - Geben Sie Ihr Benutzer-Passwort ein")
    print("   - Die GUI öffnet sich danach")
    print()
    input("Drücken Sie Enter zum Fortfahren...")

if __name__ == "__main__":
    show_policykit_info()
    
    # Patch für Demo-Modus
    from core.update_manager import UpdateManager
    from core.apt_manager import APTManager
    from core.flatpak_manager import FlatpakManager
    import time
    
    # Einfache Demo-Updates
    demo_updates = [
        {
            'name': 'demo-security-update',
            'current_version': '1.0.0',
            'new_version': '1.0.1',
            'source': 'apt',
            'type': 'security',
            'is_security': True,
            'description': 'Demo security update',
            'size': '2.1 MB'
        },
        {
            'name': 'demo-regular-update', 
            'current_version': '2.3.4',
            'new_version': '2.3.5',
            'source': 'apt',
            'type': 'regular',
            'is_security': False,
            'description': 'Demo regular update',
            'size': '15.3 MB'
        }
    ]
    
    installed_packages = set()
    
    def demo_apt_updates(self):
        return [u for u in demo_updates if u['name'] not in installed_packages]
    
    def demo_flatpak_updates(self):
        return []  # Keine Flatpak-Updates für diese Demo
    
    def demo_apt_install(self, update):
        self.logger.info(f"[DEMO] Installing: {update['name']}")
        time.sleep(1)  # Simulation
        installed_packages.add(update['name'])
        self.logger.info(f"[DEMO] Successfully installed: {update['name']}")
        return True
    
    # Apply patches
    APTManager.get_updates = demo_apt_updates
    FlatpakManager.get_updates = demo_flatpak_updates
    APTManager.install_update = demo_apt_install
    
    print("\n🎬 Starte GUP Demo mit PolicyKit...")
    print("💡 Das Passwort-Fenster kommt vom System (PolicyKit)")
    
    from main import main
    main()