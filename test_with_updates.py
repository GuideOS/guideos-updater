#!/usr/bin/env python3
"""
Test script to simulate available updates for demonstration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create mock updates for testing
def create_test_updates():
    return [
        {
            'name': 'firefox',
            'current_version': '115.0',
            'new_version': '115.2.1',
            'source': 'apt',
            'type': 'security',
            'is_security': True,
            'description': 'Mozilla Firefox web browser - security update',
            'size': '89.2 MB'
        },
        {
            'name': 'libreoffice-common',
            'current_version': '7.5.1',
            'new_version': '7.5.2',
            'source': 'apt',
            'type': 'regular',
            'is_security': False,
            'description': 'LibreOffice office suite - common files',
            'size': '45.1 MB'
        },
        {
            'name': 'org.gimp.GIMP',
            'current_version': '2.10.34',
            'new_version': '2.10.36',
            'source': 'flatpak',
            'type': 'application',
            'is_security': False,
            'description': 'GNU Image Manipulation Program',
            'size': '156 MB',
            'branch': 'stable',
            'origin': 'flathub'
        },
        {
            'name': 'curl',
            'current_version': '7.88.1',
            'new_version': '7.88.2',
            'source': 'apt',
            'type': 'security',
            'is_security': True,
            'description': 'Command line tool for transferring data - security update',
            'size': '2.1 MB'
        }
    ]

if __name__ == "__main__":
    # Monkey patch the update managers for demonstration
    from core.update_manager import UpdateManager
    from core.apt_manager import APTManager
    from core.flatpak_manager import FlatpakManager
    import time
    
    # Override get_updates methods
    def mock_apt_updates(self):
        test_updates = create_test_updates()
        return [u for u in test_updates if u['source'] == 'apt']
    
    def mock_flatpak_updates(self):
        test_updates = create_test_updates()
        return [u for u in test_updates if u['source'] == 'flatpak']
    
    # Override install methods to simulate successful installation
    def mock_apt_install(self, update):
        self.logger.info(f"[MOCK] Installing APT package: {update['name']}")
        time.sleep(0.5)  # Simulate installation time
        self.logger.info(f"[MOCK] Successfully installed {update['name']}")
        return True
    
    def mock_flatpak_install(self, update):
        self.logger.info(f"[MOCK] Installing Flatpak app: {update['name']}")
        time.sleep(0.5)  # Simulate installation time
        self.logger.info(f"[MOCK] Successfully updated {update['name']}")
        return True
    
    # Create a tracking variable for installed packages
    installed_packages = set()
    
    def mock_apt_updates_after_install(self):
        test_updates = create_test_updates()
        # Filter out installed packages
        return [u for u in test_updates if u['source'] == 'apt' and u['name'] not in installed_packages]
    
    def mock_flatpak_updates_after_install(self):
        test_updates = create_test_updates()
        # Filter out installed packages
        return [u for u in test_updates if u['source'] == 'flatpak' and u['name'] not in installed_packages]
    
    def mock_apt_install_with_tracking(self, update):
        self.logger.info(f"[MOCK] Installing APT package: {update['name']}")
        time.sleep(0.5)  # Simulate installation time
        installed_packages.add(update['name'])
        self.logger.info(f"[MOCK] Successfully installed {update['name']}")
        return True
    
    def mock_flatpak_install_with_tracking(self, update):
        self.logger.info(f"[MOCK] Installing Flatpak app: {update['name']}")
        time.sleep(0.5)  # Simulate installation time
        installed_packages.add(update['name'])
        self.logger.info(f"[MOCK] Successfully updated {update['name']}")
        return True
    
    # Apply patches
    APTManager.get_updates = mock_apt_updates_after_install
    FlatpakManager.get_updates = mock_flatpak_updates_after_install
    APTManager.install_update = mock_apt_install_with_tracking
    FlatpakManager.install_update = mock_flatpak_install_with_tracking
    
    print("Starting GUP with test data...")
    print("Note: This is a demonstration mode with simulated updates")
    from main import main
    main()