"""
Authentication utilities for sudo operations
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
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
        dialog = Gtk.Dialog(
            title=_("Authentication Required"),
            parent=self.parent_window,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        
        dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("Authenticate"), Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        
        # Content area
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_left(20)
        content_area.set_margin_right(20)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        
        # Icon and message
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Authentication icon
        icon = Gtk.Image.new_from_icon_name("dialog-password", Gtk.IconSize.DIALOG)
        hbox.pack_start(icon, False, False, 0)
        
        # Message box
        vbox_msg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        title_label = Gtk.Label()
        title_label.set_markup(f"<b>{message}</b>")
        title_label.set_halign(Gtk.Align.START)
        vbox_msg.pack_start(title_label, False, False, 0)
        
        desc_label = Gtk.Label()
        desc_label.set_text(_("Please enter your password to continue."))
        desc_label.set_halign(Gtk.Align.START)
        vbox_msg.pack_start(desc_label, False, False, 0)
        
        hbox.pack_start(vbox_msg, True, True, 0)
        content_area.pack_start(hbox, False, False, 0)
        
        # Password entry
        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        password_label = Gtk.Label(_("Password:"))
        password_label.set_size_request(80, -1)
        password_box.pack_start(password_label, False, False, 0)
        
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)  # Hide password
        self.password_entry.set_invisible_char('●')
        self.password_entry.set_activates_default(True)
        password_box.pack_start(self.password_entry, True, True, 0)
        
        content_area.pack_start(password_box, False, False, 0)
        
        # Show caps lock warning
        self.caps_warning = Gtk.Label()
        self.caps_warning.set_markup(f'<span color="orange">{_("⚠ Caps Lock is on")}</span>')
        self.caps_warning.set_no_show_all(True)
        content_area.pack_start(self.caps_warning, False, False, 0)
        
        # Connect signals
        self.password_entry.connect("key-press-event", self._on_key_press)
        
        dialog.show_all()
        self.password_entry.grab_focus()
        
        response = dialog.run()
        password = self.password_entry.get_text()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK and password:
            return self._verify_password(password)
        
        return False
    
    def _on_key_press(self, entry, event):
        """Handle key press events in password entry"""
        # Check caps lock status
        try:
            if hasattr(event, 'state') and event.state & Gdk.ModifierType.LOCK_MASK:
                self.caps_warning.show()
            else:
                self.caps_warning.hide()
        except:
            # Fallback if Gdk access fails
            pass
    
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
        dialog = Gtk.MessageDialog(
            parent=self.parent_window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Authentication Failed"
        )
        dialog.format_secondary_text("The password you entered is incorrect. Please try again.")
        dialog.run()
        dialog.destroy()
    
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