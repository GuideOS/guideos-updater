"""
Flatpak Package Manager Interface
Handles Flatpak application operations and updates
"""

import subprocess
import json
from utils.logger import Logger

class FlatpakManager:
    """Manager for Flatpak package operations"""
    
    def __init__(self):
        self.logger = Logger()
    
    def get_updates(self):
        """Get list of available Flatpak updates"""
        try:
            self.logger.info("Checking for Flatpak updates...")
            
            # Check if flatpak is installed
            if not self._is_flatpak_available():
                self.logger.info("Flatpak is not installed or available")
                return []
            
            # Update Flatpak repositories
            subprocess.run(['flatpak', 'update', '--appstream'], 
                         capture_output=True, check=True)
            
            # Get list of available updates
            result = subprocess.run(['flatpak', 'remote-ls', '--updates', '--columns=application,name,version,branch,origin'], 
                                  capture_output=True, text=True)
            
            updates = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 5:
                    app_id = parts[0]  # This is the actual flatpak ID (e.g., org.gimp.GIMP)
                    app_name = parts[1]  # This is the display name (e.g., GNU Image Manipulation Program)
                    version = parts[2]
                    branch = parts[3]
                    origin = parts[4]
                    
                    # Get current version
                    current_version = self._get_current_version(app_id)
                    
                    update = {
                        'name': app_name,  # Display name for UI
                        'app_id': app_id,  # Flatpak ID for commands
                        'current_version': current_version,
                        'new_version': version,
                        'source': 'flatpak',
                        'type': 'application',
                        'is_security': False,
                        'branch': branch,
                        'origin': origin,
                        'description': self._get_app_description(app_id),
                        'size': self._get_app_size(app_id, version)
                    }
                    updates.append(update)
            
            self.logger.info(f"Found {len(updates)} Flatpak updates")
            return updates
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting Flatpak updates: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in Flatpak manager: {e}")
            return []
    
    def install_update(self, update):
        """Install a specific Flatpak update"""
        try:
            self.logger.info(f"Installing Flatpak app: {update['name']}")
            
            # Use app_id for the actual flatpak command, not the display name
            app_identifier = update.get('app_id', update['name'])
            cmd = ['flatpak', 'update', '-y', app_identifier]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully updated {update['name']} ({app_identifier})")
                return True
            else:
                self.logger.error(f"Failed to update {update['name']} ({app_identifier}): {result.stderr}")
                return False
                
        except Exception as e:
            app_identifier = update.get('app_id', update['name'])
            self.logger.error(f"Error installing Flatpak update {update['name']} ({app_identifier}): {e}")
            return False
    
    def _is_flatpak_available(self):
        """Check if Flatpak is available on the system"""
        try:
            subprocess.run(['flatpak', '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_current_version(self, app_id):
        """Get currently installed version of a Flatpak app"""
        try:
            result = subprocess.run(['flatpak', 'list', '--app', '--columns=application,version'], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                parts = line.split('\t')
                if len(parts) >= 2 and parts[0] == app_id:
                    return parts[1]
            
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_app_description(self, app_id):
        """Get Flatpak application description"""
        try:
            result = subprocess.run(['flatpak', 'info', app_id], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.startswith('Description:'):
                    return line.split(':', 1)[1].strip()
            
            return "No description available"
        except:
            return "No description available"
    
    def _get_app_size(self, app_id, version):
        """Get Flatpak application size"""
        try:
            result = subprocess.run(['flatpak', 'info', app_id], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if 'Size:' in line:
                    size_info = line.split(':', 1)[1].strip()
                    return size_info
            
            return "Unknown"
        except:
            return "Unknown"