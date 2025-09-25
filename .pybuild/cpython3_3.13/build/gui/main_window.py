"""
Main GUI Window for GuideOS Updater
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, Notify

from utils.logger import Logger
from utils.i18n import _

class MainWindow:
    """Main window class for the update manager GUI"""
    
    def __init__(self, update_manager):
        self.update_manager = update_manager
        self.logger = Logger()
        self.selected_updates = []
        
        # Create main window
        self.window = Gtk.Window()
        self.window.set_title(_("GuideOS Updater"))
        self.window.set_default_size(800, 600)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
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
        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(vbox)
        
        # Header bar
        self._create_header_bar(vbox)
        
        # Status bar
        self._create_status_bar(vbox)
        
        # Main content area
        self._create_content_area(vbox)
        
        # Progress bar (initially hidden)
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_no_show_all(True)
        vbox.pack_start(self.progress_bar, False, False, 0)
        
        # Button area
        self._create_button_area(vbox)
    
    def _create_header_bar(self, parent):
        """Create header bar with title and refresh button"""
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title(_("GuideOS Update Manager"))
        #header_bar.set_subtitle("System Update Manager")
        
        # Refresh button
        self.refresh_button = Gtk.Button()
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        self.refresh_button.set_image(refresh_icon)
        self.refresh_button.set_tooltip_text(_("Refresh update list"))
        header_bar.pack_start(self.refresh_button)
        
        self.window.set_titlebar(header_bar)
    
    def _create_status_bar(self, parent):
        """Create status information bar"""
        self.status_frame = Gtk.Frame()
        self.status_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        status_box.set_margin_left(10)
        status_box.set_margin_right(10)
        status_box.set_margin_top(5)
        status_box.set_margin_bottom(5)
        
        self.status_label = Gtk.Label()
        self.status_label.set_markup(f"<b>{_('Ready')}</b>")
        self.status_label.set_halign(Gtk.Align.START)
        
        self.update_count_label = Gtk.Label()
        self.update_count_label.set_halign(Gtk.Align.END)
        
        status_box.pack_start(self.status_label, True, True, 0)
        status_box.pack_end(self.update_count_label, False, False, 0)
        
        self.status_frame.add(status_box)
        parent.pack_start(self.status_frame, False, False, 0)
    
    def _create_content_area(self, parent):
        """Create main content area with update list"""
        # Scrolled window for the tree view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_margin_left(10)
        scrolled.set_margin_right(10)
        scrolled.set_margin_top(10)
        scrolled.set_margin_bottom(10)
        
        # Create tree view for updates
        self.tree_view = Gtk.TreeView()
        self.tree_view.set_headers_visible(True)
        self.tree_view.set_headers_clickable(True)
        self.tree_view.set_rules_hint(True)
        
        # Create list store (columns: selected, name, current_version, new_version, source, type, size)
        self.list_store = Gtk.ListStore(bool, str, str, str, str, str, str, object)
        self.tree_view.set_model(self.list_store)
        
        # Create columns
        self._create_columns()
        
        scrolled.add(self.tree_view)
        parent.pack_start(scrolled, True, True, 0)
    
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
        button_box.set_margin_left(10)
        button_box.set_margin_right(10)
        button_box.set_margin_top(10)
        button_box.set_margin_bottom(10)
        
        # Select All button
        self.select_all_button = Gtk.Button.new_with_label(_("Select All"))
        button_box.pack_start(self.select_all_button, False, False, 0)
        
        # Select None button
        self.select_none_button = Gtk.Button.new_with_label(_("Select None"))
        button_box.pack_start(self.select_none_button, False, False, 0)
        
        # Spacer
        button_box.pack_start(Gtk.Box(), True, True, 0)
        
        # Install Updates button
        self.install_button = Gtk.Button.new_with_label(_("Install Updates"))
        self.install_button.get_style_context().add_class("suggested-action")
        self.install_button.set_sensitive(False)
        button_box.pack_end(self.install_button, False, False, 0)
        
        parent.pack_start(button_box, False, False, 0)
    
    def _setup_callbacks(self):
        """Setup callback connections"""
        self.window.connect("destroy", Gtk.main_quit)
        self.refresh_button.connect("clicked", self._on_refresh_clicked)
        self.select_all_button.connect("clicked", self._on_select_all_clicked)
        self.select_none_button.connect("clicked", self._on_select_none_clicked)
        self.install_button.connect("clicked", self._on_install_clicked)
    
    def connect_signals(self):
        """Connect external signals"""
        pass
    
    def show(self):
        """Show the main window"""
        self.window.show_all()
        # Start initial refresh (only if update_manager is available)
        if self.update_manager:
            self.status_label.set_markup(f"<b>{_('Searching for updates...')}</b>")
            self.refresh_button.set_sensitive(False)
            self.update_manager.refresh_updates()
    
    # Event handlers
    def _on_refresh_clicked(self, button):
        """Handle refresh button click"""
        if not self.update_manager:
            return
        self.refresh_button.set_sensitive(False)
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
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Install {} updates?").format(len(self.selected_updates))
        )
        dialog.format_secondary_text(_("This will install the selected updates. Continue?"))
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            self._start_installation()
    
    def _on_update_toggled(self, renderer, path):
        """Handle update selection toggle"""
        self.list_store[path][0] = not self.list_store[path][0]
        self._update_selected_updates()
    
    def _start_installation(self):
        """Start the installation process"""
        if not self.update_manager:
            return
        self.install_button.set_sensitive(False)
        self.refresh_button.set_sensitive(False)
        self.progress_bar.show()
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
    
    def _on_refresh_complete(self):
        """Handle refresh complete event"""
        self.refresh_button.set_sensitive(True)
        self.status_label.set_markup(f"<b>{_('Ready')}</b>")
    
    def _on_update_progress(self, progress, package_name):
        """Handle update progress event"""
        self.progress_bar.set_fraction(progress / 100.0)
        self.status_label.set_markup(f"<b>{_('Installing: {}').format(package_name)}</b>")
    
    def _on_update_complete(self, success):
        """Handle update complete event"""
        self.progress_bar.hide()
        self.install_button.set_sensitive(True)
        self.refresh_button.set_sensitive(True)
        
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
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=_("Updates Completed Successfully!")
        )
        
        # Get update count for the message
        update_count = len(self.selected_updates)
        
        dialog.format_secondary_text(
            _("{} updates have been installed successfully.\n\n"
              "Your system is now up to date. Some updates may require "
              "a system restart to take full effect.").format(update_count)
        )
        
        # Set dialog icon
        try:
            dialog.set_icon_name("guidos-updater")
        except:
            pass
        
        dialog.run()
        dialog.destroy()
    
    def _show_error_dialog(self):
        """Show error popup dialog after failed update"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=_("Update Installation Failed!")
        )
        
        dialog.format_secondary_text(
            _("Some updates could not be installed successfully.\n\n"
              "This might be due to:\n"
              "• Network connection issues\n"
              "• Package conflicts\n"
              "• Insufficient disk space\n"
              "• Permission problems\n\n"
              "Please check the system logs for more details and try again.")
        )
        
        # Set dialog icon
        try:
            dialog.set_icon_name("dialog-error")
        except:
            pass
        
        dialog.run()
        dialog.destroy()