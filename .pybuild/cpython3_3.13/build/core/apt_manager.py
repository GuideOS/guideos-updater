"""
APT Package Manager Interface
Handles APT package operations and updates
"""

import subprocess
import json
import re
import os
import time
from utils.logger import Logger
from utils.policykit import PolicyKitManager
from utils.auth import SudoAuthenticator

class APTManager:
    """Manager for APT package operations"""
    
    def __init__(self, parent_window=None):
        self.logger = Logger()
        self.policykit = PolicyKitManager()
        self.authenticator = SudoAuthenticator(parent_window)
        
        # Import config settings
        try:
            from config import USE_POLICYKIT, POLICYKIT_FOR_CACHE_UPDATE, POLICYKIT_FOR_INSTALL
            self.use_policykit = USE_POLICYKIT and self.policykit.is_pkexec_available()
            self.policykit_for_cache = POLICYKIT_FOR_CACHE_UPDATE
            self.policykit_for_install = POLICYKIT_FOR_INSTALL
        except ImportError:
            self.use_policykit = self.policykit.is_pkexec_available()
            self.policykit_for_cache = False  # Don't use PolicyKit for cache updates by default
            self.policykit_for_install = True
    
    def get_updates(self):
        """Get list of available APT updates"""
        try:
            self.logger.info("Checking for APT updates...")
            
            # Always update the package cache first to ensure we have the latest information
            self.logger.info("Updating APT package cache...")
            success = self._update_package_cache()
            
            if not success:
                self.logger.error("Failed to update package lists")
                # Still try to get updates with existing cache
                self.logger.info("Continuing with existing package cache...")
            
            # Get list of upgradable packages
            result = subprocess.run(['apt', 'list', '--upgradable'], 
                                  capture_output=True, text=True)
            
            updates = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if not line.strip():
                    continue
                
                # Parse package info
                parts = line.split()
                if len(parts) >= 3:
                    package_name = parts[0].split('/')[0]
                    new_version = parts[1]
                    current_version = parts[5] if len(parts) > 5 else "unknown"
                    
                    # Check if it's a security update
                    is_security = self._is_security_update(package_name)
                    
                    update = {
                        'name': package_name,
                        'current_version': current_version,
                        'new_version': new_version,
                        'source': 'apt',
                        'type': 'security' if is_security else 'regular',
                        'is_security': is_security,
                        'description': self._get_package_description(package_name),
                        'size': self._get_package_size(package_name)
                    }
                    updates.append(update)
            
            self.logger.info(f"Found {len(updates)} APT updates")
            return updates
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting APT updates: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in APT manager: {e}")
            return []
    
    def _update_package_cache(self):
        """Update the APT package cache"""
        try:
            # Use PolicyKit if specifically enabled for cache updates
            if self.use_policykit and self.policykit_for_cache:
                self.logger.info("Updating package cache with PolicyKit...")
                success, output = self.policykit.update_package_cache()
                if not success:
                    self.logger.warning(f"PolicyKit update failed, trying sudo: {output}")
                    success, output = self.authenticator.run_sudo_command(['apt', 'update'])
                return success
            else:
                # Try to update cache with sudo authentication
                self.logger.info("Updating package cache with sudo...")
                success, output = self.authenticator.run_sudo_command(['apt', 'update'])
                if success:
                    self.logger.info("APT package cache updated successfully")
                else:
                    self.logger.error(f"Failed to update APT cache: {output}")
                return success
                
        except Exception as e:
            self.logger.error(f"Error updating APT cache: {e}")
            return False
    
    def install_update(self, update):
        """Install a specific APT update"""
        try:
            self.logger.info(f"Installing APT package: {update['name']}")
            
            # Try to install the specific version first, then fallback to package name only
            attempts = []
            
            # Attempt 1: Specific version if available
            if '=' not in update['new_version'] and update['new_version'] != 'unknown':
                attempts.append(f"{update['name']}={update['new_version']}")
            
            # Attempt 2: Just the package name (let APT choose the best version)
            attempts.append(update['name'])
            
            for attempt, package_spec in enumerate(attempts, 1):
                self.logger.info(f"Installation attempt {attempt}: {package_spec}")
                
                # Use PolicyKit for installation if enabled
                if self.use_policykit and self.policykit_for_install:
                    success, output = self.policykit.install_packages([package_spec])
                    if not success:
                        self.logger.warning(f"PolicyKit install failed, trying sudo: {output}")
                        cmd = ['apt', 'install', '-y', package_spec]
                        success, output = self.authenticator.run_sudo_command(cmd)
                else:
                    cmd = ['apt', 'install', '-y', package_spec]
                    success, output = self.authenticator.run_sudo_command(cmd)
                
                if success:
                    self.logger.info(f"Successfully installed {update['name']}")
                    return True
                else:
                    self.logger.warning(f"Attempt {attempt} failed for {package_spec}: {output}")
                    if attempt < len(attempts):
                        self.logger.info(f"Trying fallback installation method...")
                    
            self.logger.error(f"All installation attempts failed for {update['name']}")
            return False
                
        except Exception as e:
            self.logger.error(f"Error installing APT update {update['name']}: {e}")
            return False
    
    def _is_security_update(self, package_name):
        """Check if a package update is security-related"""
        try:
            # Check if package is in security repository
            result = subprocess.run(['apt-cache', 'policy', package_name], 
                                  capture_output=True, text=True)
            
            return 'security' in result.stdout.lower()
        except:
            return False
    
    def _get_package_description(self, package_name):
        """Get package description"""
        try:
            result = subprocess.run(['apt-cache', 'show', package_name], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.startswith('Description:'):
                    return line.split(':', 1)[1].strip()
            
            return "No description available"
        except:
            return "No description available"
    
    def _get_package_size(self, package_name):
        """Get package download size"""
        try:
            result = subprocess.run(['apt-cache', 'show', package_name], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.startswith('Size:'):
                    size_bytes = int(line.split(':', 1)[1].strip())
                    return self._format_size(size_bytes)
            
            return "Unknown"
        except:
            return "Unknown"
    
    def _format_size(self, bytes_size):
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"