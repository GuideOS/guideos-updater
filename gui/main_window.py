"""
Main GUI Window for GuideOS Updater
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk, Notify

from utils.logger import Logger
from utils.i18n import _

class MainWindow:
    """Main window class for the update manager GUI"""
    
    def __init__(self, update_manager):
        self.update_manager = update_manager
        self.logger = Logger()
        self.selected_updates = []
        
        # Create main window
        self.window = Adw.ApplicationWindow()
        self.window.set_title(_("GuideOS Updater"))
        self.window.set_default_size(800, 600)
        
        # Set window icon
        try:
            self.window.set_icon_name("guidos-updater")
        except:
            pass
        
        # Create UI
        self._create_ui()
        self._setup_callbacks()
        
        # Connect to update manager signals (only if update_manager is not None)
        if self.update_manager:
            self._connect_update_manager_signals()
    
    def set_update_manager(self, update_manager):
        """Set the update manager and connect signals"""
        self.update_manager = update_manager
        self._connect_update_manager_signals()
    
    def _connect_update_manager_signals(self):
        """Connect to update manager signals"""
        self.update_manager.add_callback('updates_found', self._on_updates_found)
        self.update_manager.add_callback('refresh_complete', self._on_refresh_complete)
        self.update_manager.add_callback('update_progress', self._on_update_progress)
        self.update_manager.add_callback('update_complete', self._on_update_complete)
    
    def _create_ui(self):
        """Create the user interface"""
        # Create toolbar view for better libadwaita integration
        toolbar_view = Adw.ToolbarView()
        
        # Header bar
        header_bar = self._create_header_bar()
        toolbar_view.add_top_bar(header_bar)
        
        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Status bar
        self._create_status_bar(vbox)
        
        # Main content area
        self._create_content_area(vbox)
        
        # Progress bar (initially hidden)
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        vbox.append(self.progress_bar)
        
        # Button area
        self._create_button_area(vbox)
        
        toolbar_view.set_content(vbox)
        self.window.set_content(toolbar_view)
    
    def _create_header_bar(self):
        """Create header bar with title and refresh button"""
        header_bar = Adw.HeaderBar()
        
        # Refresh button
        self.refresh_button = Gtk.Button()
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic")
        self.refresh_button.set_child(refresh_icon)
        self.refresh_button.set_tooltip_text(_("Refresh update list"))
        header_bar.pack_start(self.refresh_button)
        
        return header_bar
    
    def _create_status_bar(self, parent):
        """Create status information bar"""
        self.status_frame = Gtk.Frame()
        self.status_frame.set_margin_start(10)
        self.status_frame.set_margin_end(10)
        self.status_frame.set_margin_top(10)
        
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        status_box.set_margin_start(10)
        status_box.set_margin_end(10)
        status_box.set_margin_top(5)
        status_box.set_margin_bottom(5)
        
        # Create spinner for loading animation (initially hidden)
        self.status_spinner = Gtk.Spinner()
        self.status_spinner.set_size_request(24, 24)
        self.status_spinner.set_visible(False)
        
        self.status_label = Gtk.Label()
        self.status_label.set_markup(f"<b>{_('Ready')}</b>")
        self.status_label.set_halign(Gtk.Align.START)
        
        self.update_count_label = Gtk.Label()
        self.update_count_label.set_halign(Gtk.Align.END)
        
        status_box.append(self.status_spinner)
        status_box.append(self.status_label)
        # Spacer box for expanding
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        status_box.append(spacer)
        status_box.append(self.update_count_label)
        
        self.status_frame.set_child(status_box)
        parent.append(self.status_frame)
    
    def _create_content_area(self, parent):
        """Create main content area with update list"""
        # Scrolled window for the tree view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_margin_start(10)
        scrolled.set_margin_end(10)
        scrolled.set_margin_top(10)
        scrolled.set_margin_bottom(10)
        
        # Create tree view for updates
        self.tree_view = Gtk.TreeView()
        self.tree_view.set_headers_visible(True)
        self.tree_view.set_headers_clickable(True)
        
        # Create list store (columns: selected, name, current_version, new_version, source, type, size)
        self.list_store = Gtk.ListStore(bool, str, str, str, str, str, str, object)
        self.tree_view.set_model(self.list_store)
        
        # Create columns
        self._create_columns()
        
        scrolled.set_child(self.tree_view)
        parent.append(scrolled)
    
    def _create_columns(self):
        """Create columns for the tree view"""
        # Selection column
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self._on_update_toggled)
        column_select = Gtk.TreeViewColumn(_("Select"), renderer_toggle, active=0)
        self.tree_view.append_column(column_select)
        
        # Package name column
        renderer_text = Gtk.CellRendererText()
        column_name = Gtk.TreeViewColumn(_("Package"), renderer_text, text=1)
        column_name.set_resizable(True)
        column_name.set_min_width(200)
        self.tree_view.append_column(column_name)
        
        # Current version column
        renderer_text = Gtk.CellRendererText()
        column_current = Gtk.TreeViewColumn(_("Current Version"), renderer_text, text=2)
        column_current.set_resizable(True)
        self.tree_view.append_column(column_current)
        
        # New version column
        renderer_text = Gtk.CellRendererText()
        column_new = Gtk.TreeViewColumn(_("New Version"), renderer_text, text=3)
        column_new.set_resizable(True)
        self.tree_view.append_column(column_new)
        
        # Source column
        renderer_text = Gtk.CellRendererText()
        column_source = Gtk.TreeViewColumn(_("Source"), renderer_text, text=4)
        column_source.set_resizable(True)
        self.tree_view.append_column(column_source)
        
        # Type column
        renderer_text = Gtk.CellRendererText()
        column_type = Gtk.TreeViewColumn(_("Type"), renderer_text, text=5)
        column_type.set_resizable(True)
        self.tree_view.append_column(column_type)
        
        # Size column
        renderer_text = Gtk.CellRendererText()
        column_size = Gtk.TreeViewColumn(_("Size"), renderer_text, text=6)
        column_size.set_resizable(True)
        self.tree_view.append_column(column_size)
    
    def _create_button_area(self, parent):
        """Create button area at bottom"""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_margin_start(10)
        button_box.set_margin_end(10)
        button_box.set_margin_top(10)
        button_box.set_margin_bottom(10)
        
        # Select All button
        self.select_all_button = Gtk.Button.new_with_label(_("Select All"))
        button_box.append(self.select_all_button)
        
        # Select None button
        self.select_none_button = Gtk.Button.new_with_label(_("Select None"))
        button_box.append(self.select_none_button)
        
        # Spacer
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        button_box.append(spacer)
        
        # Install Updates button
        self.install_button = Gtk.Button.new_with_label(_("Install Updates"))
        self.install_button.add_css_class("suggested-action")
        self.install_button.set_sensitive(False)
        button_box.append(self.install_button)
        
        parent.append(button_box)
    
    def _setup_callbacks(self):
        """Setup callback connections"""
        self.refresh_button.connect("clicked", self._on_refresh_clicked)
        self.select_all_button.connect("clicked", self._on_select_all_clicked)
        self.select_none_button.connect("clicked", self._on_select_none_clicked)
        self.install_button.connect("clicked", self._on_install_clicked)
    
    def connect_signals(self):
        """Connect external signals"""
        pass
    
    def show(self):
        """Show the main window"""
        self.window.present()
        # Start initial refresh (only if update_manager is available)
        if self.update_manager:
            self.status_spinner.set_visible(True)
            self.status_spinner.start()
            self.status_label.set_markup(f"<b>{_('Searching for updates...')}</b>")
            self.refresh_button.set_sensitive(False)
            self.update_manager.refresh_updates()
    
    # Event handlers
    def _on_refresh_clicked(self, button):
        """Handle refresh button click"""
        if not self.update_manager:
            return
        self.refresh_button.set_sensitive(False)
        self.status_spinner.set_visible(True)
        self.status_spinner.start()
        self.status_label.set_markup(f"<b>{_('Searching for updates...')}</b>")
        self.update_manager.refresh_updates()
    
    def _on_select_all_clicked(self, button):
        """Handle select all button click"""
        for row in self.list_store:
            row[0] = True
        self._update_selected_updates()
    
    def _on_select_none_clicked(self, button):
        """Handle select none button click"""
        for row in self.list_store:
            row[0] = False
        self._update_selected_updates()
    
    def _on_install_clicked(self, button):
        """Handle install updates button click"""
        if not self.selected_updates:
            return
        
        # Show confirmation dialog
        dialog = Adw.MessageDialog.new(self.window)
        dialog.set_heading(_("Install {} updates?").format(len(self.selected_updates)))
        dialog.set_body(_("This will install the selected updates. Continue?"))
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("install", _("Install"))
        dialog.set_response_appearance("install", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("install")
        dialog.set_close_response("cancel")
        
        dialog.connect("response", self._on_install_dialog_response)
        dialog.present()
    
    def _on_install_dialog_response(self, dialog, response):
        """Handle install confirmation dialog response"""
        if response == "install":
            self._start_installation()
    
    def _on_update_toggled(self, renderer, path):
        """Handle update selection toggle"""
        self.list_store[path][0] = not self.list_store[path][0]
        self._update_selected_updates()
    
    def _start_installation(self):
        """Start the installation process"""
        if not self.update_manager:
            return
        # Disable all interactive elements during update
        self.install_button.set_sensitive(False)
        self.refresh_button.set_sensitive(False)
        self.select_all_button.set_sensitive(False)
        self.select_none_button.set_sensitive(False)
        self.tree_view.set_sensitive(False)
        self.progress_bar.set_visible(True)
        self.status_label.set_markup(f"<b>{_('Installing updates...')}</b>")
        
        self.update_manager.install_updates(self.selected_updates)
    
    def _update_selected_updates(self):
        """Update the list of selected updates"""
        self.selected_updates = []
        for row in self.list_store:
            if row[0]:  # If selected
                self.selected_updates.append(row[7])  # Update object
        
        self.install_button.set_sensitive(len(self.selected_updates) > 0)
        
        # Update button text
        if self.selected_updates:
            self.install_button.set_label(_("Install {} Updates").format(len(self.selected_updates)))
        else:
            self.install_button.set_label(_("Install Updates"))
    
    # Update manager callbacks
    def _on_updates_found(self, updates):
        """Handle updates found event"""
        self.list_store.clear()
        
        # Check if no updates are available
        if not updates or len(updates) == 0:
            self._show_no_updates_dialog()
            return
        
        for update in updates:
            self.list_store.append([
                True,   # selected - all updates selected by default
                update['name'],
                update['current_version'],
                update['new_version'],
                update['source'].upper(),
                update['type'].title(),
                update.get('size', 'Unknown'),
                update  # update object
            ])
        
        # Update selected updates since all are selected by default
        self._update_selected_updates()
        
        # Update status
        if self.update_manager:
            counts = self.update_manager.get_update_count()
            self.update_count_label.set_text(
                _("Total: {} | APT: {} | Flatpak: {} | Security: {}").format(
                    counts['total'], counts['apt'], counts['flatpak'], counts['security']
                )
            )
        else:
            self.update_count_label.set_text(_("No update manager available"))
    
    def _show_no_updates_dialog(self):
        """Show dialog when no updates are available"""
        dialog = Adw.MessageDialog.new(self.window)
        dialog.set_heading(_("System is up to date"))
        dialog.set_body(_("There are no updates available for your system.\n\nYour system is already running the latest versions of all packages."))
        dialog.add_response("close", _("Close Application"))
        dialog.set_response_appearance("close", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("close")
        
        dialog.connect("response", self._on_no_updates_dialog_response)
        dialog.present()
    
    def _on_no_updates_dialog_response(self, dialog, response):
        """Handle no updates dialog response"""
        # Close the application
        if self.window.get_application():
            self.window.get_application().quit()
        else:
            self.window.close()
    
    def _on_refresh_complete(self):
        """Handle refresh complete event"""
        self.status_spinner.stop()
        self.status_spinner.set_visible(False)
        self.refresh_button.set_sensitive(True)
        self.select_all_button.set_sensitive(True)
        self.select_none_button.set_sensitive(True)
        self.tree_view.set_sensitive(True)
        self.status_label.set_markup(f"<b>{_('Ready')}</b>")
    
    def _on_update_progress(self, progress, package_name):
        """Handle update progress event"""
        self.progress_bar.set_fraction(progress / 100.0)
        self.status_label.set_markup(f"<b>{_('Installing: {}').format(package_name)}</b>")
    
    def _on_update_complete(self, success):
        """Handle update complete event"""
        self.progress_bar.set_visible(False)
        # Re-enable all interactive elements
        self.install_button.set_sensitive(True)
        self.refresh_button.set_sensitive(True)
        self.select_all_button.set_sensitive(True)
        self.select_none_button.set_sensitive(True)
        self.tree_view.set_sensitive(True)
        
        if success:
            self.status_label.set_markup(f"<b>{_('Updates installed successfully - Refreshing list...')}</b>")
            
            # Show success popup dialog
            self._show_success_dialog()
            
            # Show notification
            notification = Notify.Notification.new(
                _("Updates Complete"),
                _("All selected updates have been installed successfully."),
                "guidos-updater"
            )
            notification.show()
            
            # Clear current selection and refresh the update list
            self.selected_updates = []
            self._update_selected_updates()
            
            # Refresh after a short delay to allow system to update
            GLib.timeout_add_seconds(2, self._delayed_refresh)
        else:
            self.status_label.set_markup(f"<b>{_('Update installation failed')}</b>")
            
            # Show error popup dialog
            self._show_error_dialog()
            
            # Show error notification
            notification = Notify.Notification.new(
                _("Update Failed"),
                _("Some updates could not be installed. Check the logs for details."),
                "dialog-error"
            )
            notification.show()
    
    def _delayed_refresh(self):
        """Delayed refresh after successful updates"""
        if self.update_manager:
            self.update_manager.refresh_updates()
        return False  # Don't repeat
    
    def _show_success_dialog(self):
        """Show success popup dialog after successful update"""
        # Get update count for the message
        update_count = len(self.selected_updates)
        
        dialog = Adw.MessageDialog.new(self.window)
        dialog.set_heading(_("Updates Completed Successfully!"))
        dialog.set_body(
            _("{} updates have been installed successfully.\n\n"
              "Your system is now up to date. Some updates may require "
              "a system restart to take full effect.").format(update_count)
        )
        dialog.add_response("ok", _("OK"))
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("ok")
        
        dialog.present()
    
    def _show_error_dialog(self):
        """Show error popup dialog after failed update"""
        dialog = Adw.MessageDialog.new(self.window)
        dialog.set_heading(_("Update Installation Failed!"))
        dialog.set_body(
            _("Some updates could not be installed successfully.\n\n"
              "This might be due to:\n"
              "• Network connection issues\n"
              "• Package conflicts\n"
              "• Insufficient disk space\n"
              "• Permission problems\n\n"
              "Please check the system logs for more details and try again.")
        )
        dialog.add_response("ok", _("OK"))
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("ok")
        
        dialog.present()