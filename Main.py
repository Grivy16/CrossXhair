import sys
import threading
from PyQt6.QtCore import Qt, QCoreApplication, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from tkinter import filedialog, messagebox
from datetime import datetime
import subprocess
import win32gui
import win32process
import time
import psutil
from pystray import Icon, MenuItem, Menu
import CTk_Window
import PyQt_Crosshair
import win32con
import win32api
import requests

# Classe de données partagées
class SharedData(QObject):
    try :
        with open(".AppData/Data.txt", 'r') as fichier:
            Chemin_image = fichier.read()
        image_changed = pyqtSignal(str)  # Signal pour notifier le changement d'image
        image_size_changed = pyqtSignal(int)  # Signal pour notifier le changement de taille
        visibility_changed = pyqtSignal(str)  # Nouveau signal pour la visibilité

        def __init__(self):
            super().__init__()
            self.image_size = 50  # Taille par défaut de l'image
            self.visible = False  # Par défaut visible

        def set_image(self, new_path):
            self.Chemin_image = new_path
            self.image_changed.emit(self.Chemin_image)  # Émettre le signal de changement d'image

        def set_image_size(self, new_size):
            self.image_size = new_size
            self.image_size_changed.emit(self.image_size)  # Émettre le signal de changement de taille
    except Exception as e:
        with open(".AppData/log.txt", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:{e}")

def run_customtkinter_app(shared_data):
    try :
        app = CTk_Window.Setting(shared_data)
        app.mainloop()
    except Exception as e:
        with open(".AppData/log.txt", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:{e}")
        if "No such file or directory" in str(e):
            with open(".AppData/data.txt", 'w') as fichier:
                fichier.write("Image/Basique.png")
                app = Setting(shared_data)
                app.attributes('-alpha',1)
                app.mainloop()

def is_window_visible(exe_path):
    """Retourne 'on' si la fenêtre est visible, même si partiellement masquée par des fenêtres non maximisées."""
    target_exe = os.path.basename(exe_path).lower()

    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                process_exe = os.path.basename(process.exe()).lower()
                if process_exe == target_exe:
                    hwnds.append(hwnd)
            except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
                pass
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)

    if not hwnds:
        return "off"  # Aucune fenêtre trouvée

    for hwnd in hwnds:
        # Vérifier si la fenêtre est minimisée
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == win32con.SW_SHOWMINIMIZED:
            continue  # Ignorer les fenêtres minimisées

        # Si la fenêtre cible est au premier plan
        if hwnd == win32gui.GetForegroundWindow():
            return "on"

        # Vérifier les fenêtres au-dessus de la cible
        window_rect = win32gui.GetWindowRect(hwnd)
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        visible_area = (window_rect[2] - window_rect[0]) * (window_rect[3] - window_rect[1])
        total_covered_area = 0

        def check_overlap(overlay_hwnd, _):
            nonlocal total_covered_area
            if overlay_hwnd != hwnd and win32gui.IsWindowVisible(overlay_hwnd):
                overlay_rect = win32gui.GetWindowRect(overlay_hwnd)
                # Calculer la zone de chevauchement
                overlap_left = max(window_rect[0], overlay_rect[0])
                overlap_top = max(window_rect[1], overlay_rect[1])
                overlap_right = min(window_rect[2], overlay_rect[2])
                overlap_bottom = min(window_rect[3], overlay_rect[3])

                if overlap_right > overlap_left and overlap_bottom > overlap_top:
                    covered_area = (overlap_right - overlap_left) * (overlap_bottom - overlap_top)
                    total_covered_area += covered_area

            return True

        # Vérifier les fenêtres au-dessus
        win32gui.EnumWindows(check_overlap, None)

        # Si plus de 10% de la fenêtre cible reste visible, elle est considérée "on"
        visible_ratio = (visible_area - total_covered_area) / visible_area
        if visible_ratio > 0.1:  # Ajustable (10% de visibilité minimale)
            return "on"

        return "off"

    return "off"  # Fenêtre masquée ou non visible

def vérification(shared_data):
    last_state = None
    while True:
        with open(".AppData/files.txt", 'r') as fichier:
            lignes = [l.strip() for l in fichier.readlines() if l.strip()]

        current_state = "off"
        for ligne in lignes:
            status = is_window_visible(ligne)
            if status == "on":
                current_state = "on"
                break

        # Ne notifier que si l'état a changé
        if current_state != last_state:
            shared_data.visibility_changed.emit(current_state)
            last_state = current_state
            print(current_state)
        time.sleep(1)  # Réduire le délai à 1 seconde


def launch_icon():
    def launchsetting() :
        customtkinter_thread = threading.Thread(target=run_customtkinter_app, args=(shared_data,))
        customtkinter_thread.start()
    def quittéicon():
        icon.stop()
        os._exit(0)
    icon = Icon("ParamIcon", Image.open(os.path.join(os.path.dirname(__file__), ".AppData\\logo.ico")), menu=Menu(
                MenuItem("Setting", launchsetting),
                    MenuItem("Quit", quittéicon),
                ))
    icon.run()

def LastGithubRelease():
    # Remplacez 'nom-utilisateur' et 'nom-repository' par le nom du dépôt GitHub
    url = "https://api.github.com/repos/Grivy16/CrossXhair/releases/latest"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        tag_name = data.get("tag_name", "No tags found")
        return tag_name
    else:
        with open(".AppData/log.txt", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:Impossible de récupérer les informations. Vérifiez le dépôt ou votre connexion internet.")

if __name__ == "__main__":
    try :
        os.makedirs(".AppData", exist_ok=True)
        os.makedirs("Image", exist_ok=True)

        if not os.path.exists(".AppData/Data.txt"):
            with open(".AppData/Data.txt", 'w') as fichier:
                fichier.write("Image/Basique.png")
        if not os.path.exists(".AppData/log.txt"):
            with open(".AppData/log.txt", 'w') as fichier:
                fichier.close()
        if not os.path.exists(".AppData/files.txt"):
            with open(".AppData/files.txt", 'w') as fichier:
                fichier.close()
        if not os.path.exists(".AppData/Maj.txt"):
            with open(".AppData/Maj.txt", 'w') as fichier:
                fichier.write(LastGithubRelease())

        with open(".AppData/Maj.txt", 'r') as fichier:
            if LastGithubRelease() != fichier.read()
                reponse = messagebox.askyesno("Question", "Voulez-vous continuer ?")
        # Instance partagée
        shared_data = SharedData()

        vérification_thread = threading.Thread(target=vérification, args=(shared_data,))
        Launcicon = threading.Thread(target=launch_icon)
        customtkinter_thread = threading.Thread(target=run_customtkinter_app, args=(shared_data,))
        customtkinter_thread.start()

        vérification_thread.start()
        Launcicon.start()

        try :
            app = QApplication(sys.argv)
            crossair = PyQt_Crosshair.TransparentApp(shared_data)
            crossair.show()
            sys.exit(app.exec())
        except Exeption as e:
            with open(".AppData/log.txt", 'a') as fichier:
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                fichier.write(f"\n[{formatted_time}]:{e}")
        customtkinter_thread.join()
    except Exception as e:
        with open(".AppData/log.txt", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:{e}")