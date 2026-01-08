#!/usr/bin/env python3
"""
GuideOS Updater - GuideOS Update Manager
A GUI update manager for APT and Flatpak packages, similar to mintupdate.
"""

import gi
import sys
import os
import threading
import subprocess
import json
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Adw, GLib, Gio, Notify

# Initialize internationalization first
from utils.i18n import _

# Local imports
from core.update_manager import UpdateManager
from gui.main_window import MainWindow
from utils.logger import Logger

class GuideOSUpdaterApplication(Adw.Application):
    """Main application class for GuideOS Update Manager"""
    
    def __init__(self):
        super().__init__(application_id="org.guideos.updater", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.logger = Logger()
        self.logger.info("Starting GuideOS Updater")
        
        # Initialize libadwaita
        Adw.init()
        
        # Initialize notification system
        Notify.init("GuideOS Updater")
        
        self.main_window = None
        self.update_manager = None
    
    def do_activate(self):
        """Called when the application is activated"""
        if not self.main_window:
            # Create main window first
            self.main_window = MainWindow(None)
            self.main_window.window.set_application(self)
            
            # Create update manager with window reference
            self.update_manager = UpdateManager(self.main_window.window)
            
            # Set the update manager in the main window
            self.main_window.set_update_manager(self.update_manager)
            
            # Connect signals
            self.main_window.connect_signals()
        
        # Show the window
        self.main_window.show()
    
    def do_shutdown(self):
        """Called when the application is shutting down"""
        self.logger.info("Shutting down GuideOS Updater")
        Adw.Application.do_shutdown(self)

def main():
    """Main entry point"""
    if os.getuid() == 0:
        print("Error: Do not run this application as root")
        sys.exit(1)
    
    app = GuideOSUpdaterApplication()
    return app.run(None)

if __name__ == "__main__":
    sys.exit(main())