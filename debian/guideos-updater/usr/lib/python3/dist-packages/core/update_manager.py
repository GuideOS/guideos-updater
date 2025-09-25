"""
Core Update Manager
Handles APT and Flatpak update operations
"""

import subprocess
import threading
import json
import time
from gi.repository import GLib
from .apt_manager import APTManager
from .flatpak_manager import FlatpakManager
from utils.logger import Logger

class UpdateManager:
    """Central manager for handling updates from different sources"""
    
    def __init__(self, parent_window=None):
        self.logger = Logger()
        self.apt_manager = APTManager(parent_window)
        self.flatpak_manager = FlatpakManager()
        
        self.updates = []
        self.is_refreshing = False
        self.callbacks = {
            'updates_found': [],
            'refresh_complete': [],
            'update_progress': [],
            'update_complete': []
        }
    
    def add_callback(self, event, callback):
        """Add callback for specific events"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def emit_signal(self, event, *args):
        """Emit signal to all registered callbacks"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                GLib.idle_add(callback, *args)
    
    def refresh_updates(self, force_cache_update=True):
        """Refresh available updates from all sources"""
        if self.is_refreshing:
            return
        
        self.is_refreshing = True
        self.updates = []
        
        def refresh_thread():
            try:
                self.logger.info("Refreshing update information...")
                
                # Refresh APT updates (this will automatically update the cache)
                apt_updates = self.apt_manager.get_updates()
                self.updates.extend(apt_updates)
                
                # Refresh Flatpak updates
                flatpak_updates = self.flatpak_manager.get_updates()
                self.updates.extend(flatpak_updates)
                
                self.logger.info(f"Found {len(self.updates)} available updates")
                self.emit_signal('updates_found', self.updates)
                
            except Exception as e:
                self.logger.error(f"Error refreshing updates: {e}")
            finally:
                self.is_refreshing = False
                self.emit_signal('refresh_complete')
        
        thread = threading.Thread(target=refresh_thread)
        thread.daemon = True
        thread.start()
    
    def update_package_cache(self):
        """Explicitly update package cache from all sources"""
        try:
            self.logger.info("Updating package caches...")
            
            # Update APT cache
            apt_success = self.apt_manager._update_package_cache()
            
            # Update Flatpak cache (if needed)
            flatpak_success = self.flatpak_manager.update_cache() if hasattr(self.flatpak_manager, 'update_cache') else True
            
            return apt_success and flatpak_success
            
        except Exception as e:
            self.logger.error(f"Error updating package caches: {e}")
            return False
    
    def install_updates(self, selected_updates):
        """Install selected updates"""
        def install_thread():
            try:
                self.logger.info(f"Installing {len(selected_updates)} updates...")
                
                # Separate APT and Flatpak updates
                apt_updates = [update for update in selected_updates if update['source'] == 'apt']
                flatpak_updates = [update for update in selected_updates if update['source'] == 'flatpak']
                
                total_updates = len(selected_updates)
                completed = 0
                
                # Install APT updates
                for update in apt_updates:
                    self.apt_manager.install_update(update)
                    completed += 1
                    progress = (completed / total_updates) * 100
                    self.emit_signal('update_progress', progress, update['name'])
                
                # Install Flatpak updates
                for update in flatpak_updates:
                    self.flatpak_manager.install_update(update)
                    completed += 1
                    progress = (completed / total_updates) * 100
                    self.emit_signal('update_progress', progress, update['name'])
                
                self.logger.info("All updates installed successfully")
                self.emit_signal('update_complete', True)
                
            except Exception as e:
                self.logger.error(f"Error installing updates: {e}")
                self.emit_signal('update_complete', False)
        
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
    
    def get_update_count(self):
        """Get count of available updates by type"""
        apt_count = len([u for u in self.updates if u['source'] == 'apt'])
        flatpak_count = len([u for u in self.updates if u['source'] == 'flatpak'])
        security_count = len([u for u in self.updates if u.get('is_security', False)])
        
        return {
            'total': len(self.updates),
            'apt': apt_count,
            'flatpak': flatpak_count,
            'security': security_count
        }