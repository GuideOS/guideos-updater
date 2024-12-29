import subprocess
import tkinter as tk
from tkinter import Scrollbar, Listbox

def get_apt_updates():
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
            return ["APT Updates:"] + updates
        else:  # Keine Updates verfügbar
            return ["Keine APT-Updates verfügbar."]
    except Exception as e:
        return [f"Fehler beim Abrufen von APT-Updates: {str(e)}"]

def get_flatpak_updates():
    """Abrufen der Flatpak-Updates."""
    try:
        result = subprocess.run(
            ['flatpak', 'remote-ls', '--updates'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        updates = result.stdout.splitlines()
        if len(updates) > 1:  # Überschrift + mindestens ein Update
            return ["Flatpak Updates:"] + updates
        else:  # Keine Updates verfügbar
            return ["Keine Flatpak-Updates verfügbar."]
    except Exception as e:
        return [f"Fehler beim Abrufen von Flatpak-Updates: {str(e)}"]

def update_listbox():
    """Lädt Updates neu und zeigt sie in der Listbox an."""
    apt_updates = get_apt_updates()
    flatpak_updates = get_flatpak_updates()
    listbox.delete(0, tk.END)  # Listbox leeren
    for update in apt_updates + [""] + flatpak_updates:  # Updates kombinieren
        listbox.insert(tk.END, update)

# Tkinter-GUI einrichten
root = tk.Tk()
root.title("System-Updates: APT und Flatpak")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

scrollbar = Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = Listbox(frame, yscrollcommand=scrollbar.set, height=25, width=100)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=listbox.yview)

update_button = tk.Button(root, text="Aktualisieren", command=update_listbox)
update_button.pack(pady=10)

# Initiale Updates laden
update_listbox()

# Main-Loop starten
root.mainloop()
