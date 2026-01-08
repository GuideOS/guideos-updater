"""
Authentication utilities for sudo operations
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import threading
from utils.logger import Logger
from utils.i18n import _

class SudoAuthenticator:
    """Handles sudo authentication with graphical password dialog"""
    
    def __init__(self, parent_window=None):
        self.parent_window = parent_window
        self.logger = Logger()
        self._password = None
        self._authenticated = False
    
    def authenticate(self, message=None):
        """Show password dialog and authenticate with sudo"""
        if message is None:
            message = _("Administrator privileges required")
        return self._show_password_dialog(message)
    
    def _show_password_dialog(self, message):
        """Show GTK password dialog"""
        dialog = Gtk.Window()
        dialog.set_title(_("Authentication Required"))
        dialog.set_transient_for(self.parent_window)
        dialog.set_modal(True)
        dialog.set_default_size(400, -1)
        dialog.set_resizable(False)
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        
        # Icon and message
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Authentication icon
        icon = Gtk.Image.new_from_icon_name("dialog-password")
        icon.set_pixel_size(48)
        hbox.append(icon)
        
        # Message box
        vbox_msg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox_msg.set_hexpand(True)
        
        title_label = Gtk.Label()
        title_label.set_markup(f"<b>{message}</b>")
        title_label.set_halign(Gtk.Align.START)
        vbox_msg.append(title_label)
        
        desc_label = Gtk.Label()
        desc_label.set_text(_("Please enter your password to continue."))
        desc_label.set_halign(Gtk.Align.START)
        vbox_msg.append(desc_label)
        
        hbox.append(vbox_msg)
        main_box.append(hbox)
        
        # Password entry
        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        password_label = Gtk.Label(label=_("Password:"))
        password_label.set_size_request(80, -1)
        password_box.append(password_label)
        
        self.password_entry = Gtk.PasswordEntry()
        self.password_entry.set_show_peek_icon(True)
        self.password_entry.set_hexpand(True)
        password_box.append(self.password_entry)
        
        main_box.append(password_box)
        
        # Show caps lock warning
        self.caps_warning = Gtk.Label()
        self.caps_warning.set_markup(f'<span color="orange">{_("⚠ Caps Lock is on")}</span>')
        self.caps_warning.set_visible(False)
        main_box.append(self.caps_warning)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(10)
        
        cancel_button = Gtk.Button.new_with_label(_("Cancel"))
        cancel_button.connect("clicked", lambda w: dialog.close())
        button_box.append(cancel_button)
        
        auth_button = Gtk.Button.new_with_label(_("Authenticate"))
        auth_button.add_css_class("suggested-action")
        self.auth_button = auth_button
        self.dialog = dialog
        auth_button.connect("clicked", self._on_authenticate_clicked)
        button_box.append(auth_button)
        
        main_box.append(button_box)
        
        dialog.set_child(main_box)
        
        # Connect enter key to authenticate
        self.password_entry.connect("activate", lambda w: self._on_authenticate_clicked(auth_button))
        
        # Set up key event controller for caps lock detection
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        key_controller.connect("key-released", self._on_key_released)
        self.password_entry.add_controller(key_controller)
        
        # Store result
        self.auth_result = False
        self.auth_password = None
        
        dialog.present()
        
        # Run modal loop
        loop = GLib.MainLoop()
        self.main_loop = loop
        dialog.connect("close-request", lambda w: loop.quit())
        loop.run()
        
        if self.auth_password:
            return self._verify_password(self.auth_password)
        
        return False
    
    def _on_authenticate_clicked(self, button):
        """Handle authenticate button click"""
        password = self.password_entry.get_text()
        if password:
            self.auth_password = password
            self.dialog.close()
            if hasattr(self, 'main_loop'):
                self.main_loop.quit()
    
    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle key press events"""
        # Check if Caps Lock is on
        if state & Gdk.ModifierType.LOCK_MASK:
            self.caps_warning.set_visible(True)
        else:
            self.caps_warning.set_visible(False)
        return False
    
    def _on_key_released(self, controller, keyval, keycode, state):
        """Handle key release events"""
        # Check if Caps Lock is on
        if state & Gdk.ModifierType.LOCK_MASK:
            self.caps_warning.set_visible(True)
        else:
            self.caps_warning.set_visible(False)
        return False
    
    def _verify_password(self, password):
        """Verify the sudo password"""
        try:
            # Test sudo access with the provided password
            process = subprocess.Popen(
                ['sudo', '-S', 'true'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=password + '\n', timeout=10)
            
            if process.returncode == 0:
                self.logger.info("Sudo authentication successful")
                self._password = password
                self._authenticated = True
                return True
            else:
                self.logger.warning("Sudo authentication failed")
                self._show_auth_error()
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Sudo authentication timed out")
            process.kill()
            return False
        except Exception as e:
            self.logger.error(f"Error during sudo authentication: {e}")
            return False
    
    def _show_auth_error(self):
        """Show authentication error dialog"""
        dialog = Gtk.AlertDialog()
        dialog.set_message(_("Authentication Failed"))
        dialog.set_detail(_("The password you entered is incorrect. Please try again."))
        dialog.set_buttons([_("OK")])
        dialog.show(self.parent_window)
    
    def run_sudo_command(self, command):
        """Run a command with sudo using stored credentials"""
        if not self._authenticated or not self._password:
            if not self.authenticate("Administrator privileges required for this operation"):
                return False, "Authentication failed"
        
        try:
            # Run the sudo command
            process = subprocess.Popen(
                ['sudo', '-S'] + command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=self._password + '\n')
            
            if process.returncode == 0:
                return True, stdout
            else:
                return False, stderr
                
        except Exception as e:
            self.logger.error(f"Error running sudo command: {e}")
            return False, str(e)
    
    def clear_credentials(self):
        """Clear stored credentials"""
        self._password = None
        self._authenticated = False