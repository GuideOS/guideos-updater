#!/usr/bin/python3

from tkinter import *
from tkinter import ttk
import tkinter as tk
import subprocess
import os
from tkinter import Scrollbar, Listbox
import tkinter.messagebox as messagebox


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__(className="guideos-updater")
        self.title("GuideOS Updater")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        application_path = os.path.dirname(script_dir)
        self.tk.call(
            "source", f"{application_path}/guideos-updater/azure-adwaita-ttk/azure.tcl"
        )
        self.tk.call("set_theme", "light")
        # self["background"] = maincolor
        app_width = 600
        app_height = 500
        # Define Screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (app_width / 2)
        y = (screen_height / 2) - (app_height / 2)
        # self.icon is still needed for some DEs
        self.icon = tk.PhotoImage(
            file=f"/usr/share/icons/hicolor/256x256/apps/primo-di-tutto-logo.png"
        )
        self.tk.call("wm", "iconphoto", self._w, self.icon)
        self.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")
        #self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)



        self.term_logo = PhotoImage(
            file=f"{application_path}/guideos-updater/guide-os-logo-symbolic-light.png"
        )

        # Text-Widget hinzufügen
        #self.info_text = ttk.Label(self,wraplength=550,text="Möchtest du dein System aktualisieren?")
        #self.info_text.grid(row=0, column=0, padx=20, pady=10, sticky="ew")


        self.frame = ttk.LabelFrame(self, text="Aktualisierungen",padding=10)
        self.frame.grid(row=0, column=0, padx=20, pady=10,sticky="ew")

        self.scrollbar = ttk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = Listbox(self.frame, yscrollcommand=self.scrollbar.set, height=10, width=100,borderwidth=0, highlightthickness=0,)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.listbox.yview)






        # Button hinzufügen
        self.button = ttk.Button(self, text="Aktualisieren", command=self.all_up_action)
        self.button.grid(row=2, column=0, padx=20, pady=10,sticky="ew")
        # Initiale Updates laden
        self.update_listbox()
        # LabelFrame erstellen
        self.labelframe = Frame(self)
        self.labelframe.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.termf = ttk.Frame(self.labelframe)

        self.termf.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.term_logo_label = Label(
            self.termf,
            image=self.term_logo
        )
        self.term_logo_label.pack(fill="x",expand=TRUE)
        global wid
        wid = self.termf.winfo_id()


    def get_apt_updates(self):
        """Abrufen der APT-Updates."""
        try:
            result = subprocess.run(
                ['apt', 'list', '--upgradable'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            updates = result.stdout.splitlines()[1:]  # Überschrift auslassen
            if updates:  # Wenn Updates vorhanden sind
                return True, ["APT Updates:"] + updates
            else:  # Keine Updates verfügbar
                return False, ["Keine APT-Updates verfügbar."]
        except Exception as e:
            return [f"Fehler beim Abrufen von APT-Updates: {str(e)}"]

    def get_flatpak_updates(self):
        """Abrufen der Flatpak-Updates."""
        try:
            result = subprocess.run(
                ['flatpak', 'remote-ls', '--updates'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            updates = result.stdout.splitlines()
            print("Flatpak updates:", updates)  # Debug print
            if len(updates) > 1:  # Überschrift + mindestens ein Update
                return True, ["Flatpak Updates:"] + updates
            else:  # Keine Updates verfügbar
                return False, ["Keine Flatpak-Updates verfügbar."]
        except Exception as e:
            return [f"Fehler beim Abrufen von Flatpak-Updates: {str(e)}"]

    def update_listbox(self):
        """Lädt Updates neu und zeigt sie in der Listbox an."""
        apt_updates = self.get_apt_updates()
        flatpak_updates = self.get_flatpak_updates()
        print("APT updates:", apt_updates)  # Debug print
        print("Flatpak updates:", flatpak_updates)  # Debug print
        self.listbox.delete(0, tk.END)  # Listbox leeren
        for update in apt_updates[1] + [""] + flatpak_updates[1]:  # Updates kombinieren
            self.listbox.insert(tk.END, update)

        # Button deaktivieren, wenn keine Updates verfügbar sind
        if not apt_updates[0] and not flatpak_updates[0]:
            self.button.config(state=tk.DISABLED)
        else:
            self.button.config(state=tk.NORMAL)

    def all_up_action(self):
        """Passes commands for auto-generated buttons"""
        frame_width = self.termf.winfo_width()
        frame_height = self.termf.winfo_height()

        command = (
            f"xterm -into {wid} -bg Grey11 -geometry {frame_height}x{frame_width} -e "
            "\"pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY bash -c 'apt update -y && apt upgrade -y && apt autoremove -y && flatpak update -y && flatpak uninstall --unused -y && sleep 5' "
            'sleep 5 && exit; exec bash"'
        )

        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Benachrichtigung anzeigen, wenn die Aktualisierungen abgeschlossen sind
            messagebox.showinfo("Aktualisierung", "Alle Aktualisierungen wurden erfolgreich abgeschlossen.")
        except subprocess.CalledProcessError as e:
            # Fehlerbenachrichtigung anzeigen
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")

        # Beispielaufruf mit Icon und hoher Dringlichkeit
        self.update_listbox()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()