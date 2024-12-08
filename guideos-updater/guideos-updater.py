#!/usr/bin/python3

from tkinter import *
from tkinter import ttk
import tkinter as tk
import subprocess
import os

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__(className="guideos-updater")
        self.title("Aktualisierung")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        application_path = os.path.dirname(script_dir)
        self.tk.call(
            "source", f"{application_path}/guideos-updater/azure-adwaita-ttk/azure.tcl"
        )
        self.tk.call("set_theme", "light")
        # self["background"] = maincolor
        app_width = 600
        app_height = 350
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
        self.info_text = ttk.Label(self,wraplength=550,text="Möchtest du ein System aktualisieren?")
        self.info_text.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # Button hinzufügen
        self.button = ttk.Button(self, text="System aktualisieren", command=self.all_up_action)
        self.button.grid(row=1, column=0, padx=20, pady=10,sticky="ew")

        # LabelFrame erstellen
        self.labelframe = Frame(self)
        self.labelframe.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.termf = ttk.Frame(self.labelframe)

        self.termf.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.term_logo_label = Label(
            self.termf,
            image=self.term_logo
        )
        self.term_logo_label.pack(fill="x",expand=TRUE)
        global wid
        wid = self.termf.winfo_id()

    def all_up_action(self):
        """Passes commands for auto-generated buttons"""
        frame_width = self.termf.winfo_width()
        frame_height = self.termf.winfo_height()

        command = (
            f"xterm -into {wid} -bg Grey11 -geometry {frame_height}x{frame_width} -e "
            "\"pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY bash -c 'apt update -y && apt upgrade -y && apt autoremove -y && flatpak update -y && flatpak uninstall --unused -y' "
            'sleep 5 && exit; exec bash"'
        )


        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Beispielaufruf mit Icon und hoher Dringlichkeit


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
