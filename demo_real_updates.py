#!/usr/bin/env python3
"""
Demo script for GUP Update Manager with realistic APT packages
This version uses actual packages that might be available for updates
"""

import sys
import os
import subprocess

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def get_real_updates():
    """Get some real packages that commonly have updates"""
    real_updates = []
    
    # Check for some common packages that often have updates
    packages_to_check = [
        'firefox-esr', 'chromium', 'libreoffice-common', 
        'curl', 'wget', 'git', 'vim', 'nano'
    ]
    
    try:
        # Check which packages are installed and have updates
        result = subprocess.run(['apt', 'list', '--upgradable'], 
                              capture_output=True, text=True)
        
        upgradable_lines = result.stdout.strip().split('\n')[1:]  # Skip header
        
        for line in upgradable_lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    package_name = parts[0].split('/')[0]
                    new_version = parts[1]
                    current_version = parts[5] if len(parts) > 5 else "installed"
                    
                    # Add to real updates
                    update = {
                        'name': package_name,
                        'current_version': current_version,
                        'new_version': new_version,
                        'source': 'apt',
                        'type': 'regular',
                        'is_security': False,
                        'description': f"Update for {package_name}",
                        'size': "Unknown"
                    }
                    real_updates.append(update)
        
        # If no real updates found, add some common packages as examples
        if not real_updates:
            print("No real updates found. Using demonstration packages...")
            real_updates = [
                {
                    'name': 'base-files',
                    'current_version': '12.4',
                    'new_version': '12.4+deb12u2',
                    'source': 'apt',
                    'type': 'regular',
                    'is_security': False,
                    'description': 'Debian base system miscellaneous files',
                    'size': '1.2 MB'
                }
            ]
            
    except Exception as e:
        print(f"Error checking for real updates: {e}")
        return []
    
    return real_updates

if __name__ == "__main__":
    print("Starting GUP with real system updates...")
    
    # Get real updates from the system
    real_updates = get_real_updates()
    print(f"Found {len(real_updates)} real updates available")
    
    if real_updates:
        # Monkey patch with real updates
        from core.apt_manager import APTManager
        from core.flatpak_manager import FlatpakManager
        
        def real_apt_updates(self):
            return real_updates
        
        def real_flatpak_updates(self):
            # Try to get real Flatpak updates
            try:
                result = subprocess.run(['flatpak', 'remote-ls', '--updates'], 
                                      capture_output=True, text=True)
                flatpak_updates = []
                
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            app_name = parts[0]
                            update = {
                                'name': app_name,
                                'current_version': 'current',
                                'new_version': 'latest',
                                'source': 'flatpak',
                                'type': 'application',
                                'is_security': False,
                                'description': f"Flatpak update for {app_name}",
                                'size': "Unknown"
                            }
                            flatpak_updates.append(update)
                
                return flatpak_updates
            except:
                return []  # No Flatpak updates or Flatpak not available
        
        APTManager.get_updates = real_apt_updates
        FlatpakManager.get_updates = real_flatpak_updates
        
        from main import main
        main()
    else:
        print("No updates available. Try the test version instead:")
        print("python3 test_with_updates.py")