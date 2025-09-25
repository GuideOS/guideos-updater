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

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Gio, Notify

# Initialize internationalization first
from utils.i18n import _

# Local imports
from core.update_manager import UpdateManager
from gui.main_window import MainWindow
from utils.logger import Logger

class GuideOSUpdaterApplication:
    """Main application class for GuideOS Update Manager"""
    
    def __init__(self):
        self.logger = Logger()
        self.logger.info("Starting GuideOS Updater")
        
        # Initialize notification system
        Notify.init("GUP Update Manager")
        
        # Create main window first
        self.main_window = MainWindow(None)
        
        # Create update manager with window reference
        self.update_manager = UpdateManager(self.main_window.window)
        
        # Set the update manager in the main window
        self.main_window.set_update_manager(self.update_manager)
        
        # Connect signals
        self.main_window.connect_signals()
        
    def run(self):
        """Start the application"""
        try:
            self.main_window.show()
            Gtk.main()
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            self.quit()
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            self.quit()
    
    def quit(self):
        """Clean shutdown of the application"""
        self.logger.info("Shutting down GuideOS Updater")
        Gtk.main_quit()

def main():
    """Main entry point"""
    if os.getuid() == 0:
        print("Error: Do not run this application as root")
        sys.exit(1)
    
    app = GuideOSUpdaterApplication()
    app.run()

if __name__ == "__main__":
    main()