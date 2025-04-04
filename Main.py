import sys
import threading
import customtkinter as ctk
from PIL import Image, ImageTk
from PyQt6.QtCore import Qt, QCoreApplication, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *
import os
from tkinter import filedialog, messagebox
from datetime import datetime
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
import json
import subprocess
import Reload

# Classe de données partagées
class SharedData(QObject):
    # Déclaration correcte des signaux
    image_changed = pyqtSignal(str)
    image_size_changed = pyqtSignal(int)
    visibility_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        try:
            with open(".AppData/Data.json", "r", encoding="utf-8") as f:
                self.datafiles = json.load(f)
                self.Chemin_image = self.datafiles["Info"]["Crosshair"]

            self.image_size = 50  # Taille par défaut de l'image
            self.visible = False  # Par défaut visible

        except Exception as e:
            with open(".AppData/CrossXhairLog.log", 'a') as fichier:
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                fichier.write(f"\n[{formatted_time}]:{e}")

    def set_image(self, new_path):
        self.Chemin_image = new_path
        self.image_changed.emit(self.Chemin_image)  # Utilisation correcte de emit

    def set_image_size(self, new_size):
        self.image_size = new_size
        self.image_size_changed.emit(self.image_size)  # Utilisation correcte de emit

    def set_visibility(self, state):
        self.visibility_changed.emit(state)  # Utilisation correcte de emit



def run_customtkinter_app(shared_data):
    try :
        app = CTk_Window.Setting(shared_data)
        app.mainloop()
    except Exception as e:
        with open(".AppData/CrossXhairLog.log", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:{e}")
        if "No such file or directory" in str(e):
            with open(".AppData/Data.json", 'r', encoding="utf-8") as fichier:
                data = json.load(fichier)
            data["Info"]["Crosshair"] = {"Image/Basique.png"}
            with open(".AppData/Data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
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
        with open(".AppData/Data.json", "r", encoding="utf-8") as fichier:
            data = json.load(fichier)
        lignes = list(data["File"].values())

        current_state = "off"
        for ligne in lignes:
            status = is_window_visible(ligne)
            if status == "on":
                current_state = "on"
                break

        # Utilisation correcte de set_visibility
        if current_state != last_state:
            shared_data.visibility_changed.emit(current_state)
            last_state = current_state
            #print(current_state)
        time.sleep(0.5)

def vérification2(shared_data):
    while True :
        def get_foreground_window():
            """Retourne le handle de la fenêtre au premier plan."""
            return win32gui.GetForegroundWindow()

        def is_app_foreground(window_name):
            """Vérifie si l'application avec le nom de fenêtre donné est au premier plan."""
            fg_window = get_foreground_window()
            fg_window_title = win32gui.GetWindowText(fg_window)

            if window_name in fg_window_title:
                return True
            return False

        # Exemple d'utilisation
        window_name = "CrossXhair Setting"  # Remplace par le nom exact de ta fenêtre CTk
        if is_app_foreground(window_name):
            shared_data.visibility_changed.emit("on")
        else:
            shared_data.visibility_changed.emit("off")
        time.sleep(0.5)
def launch_icon():
    def launchsetting() :
        customtkinter_thread = threading.Thread(target=run_customtkinter_app, args=(shared_data,))
        customtkinter_thread.start()
    def quittéicon():
        icon.stop()
        os._exit(0)
    icon = Icon("ParamIcon", Image.open(".AppData\\logo.ico"), menu=Menu(
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
        with open(".AppData/CrossXhairLog.log", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:Impossible de récupérer les informations. Vérifiez le dépôt ou votre connexion internet.")

def DownloadGitHub_File(url, nom_local):
    response = requests.get(url)
    if response.status_code == 200:
        with open(nom_local, 'wb') as f:
            f.write(response.content)
        print(f"Fichier téléchargé : {nom_local}")
    else:
        with open(".AppData/CrossXhairLog.log", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:{response.status_code}")


def Mise_a_jour():
    DownloadGitHub_File("https://raw.githubusercontent.com/Grivy16/CrossXhair/refs/heads/main/CTk_Window.py", "CTk_Window.py")
    DownloadGitHub_File("https://raw.githubusercontent.com/Grivy16/CrossXhair/refs/heads/main/PyQt_Crosshair.py", "PyQt_Crosshair.py")
    DownloadGitHub_File("https://raw.githubusercontent.com/Grivy16/CrossXhair/refs/heads/main/CrossXhair.exe", "Main_temp.exe")
    # Attendre que le fichier soit téléchargé (si nécessaire)
    while not os.path.exists("Main_temp.exe") or os.path.getsize("Main_temp.exe") < 10000:
        time.sleep(0.1)

    # Renommer le fichier téléchargé pour éviter le conflit
    os.rename("Main_temp.exe", "CrossXhair.exe")

    with open(".AppData/Data.json", 'r', encoding="utf-8") as fichier:
        data = json.load(fichier)
    data["Info"]["Maj"] = LastGithubRelease()
    with open(".AppData/Data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    Reload.Run()

if __name__ == "__main__":
    try :
        os.makedirs(".AppData", exist_ok=True)
        os.makedirs("Image", exist_ok=True)

        data = {
            "Info": {
                "Crosshair": "Image/Basique.png",
                "Maj": LastGithubRelease()
            },
            "File": {}
        }
        if not os.path.exists(".AppData/Data.json"):
            with open(".AppData/Data.json", 'w', encoding="utf-8") as fichier:
                json.dump(data, fichier, indent=4, ensure_ascii=False)
        if not os.path.exists(".AppData/CrossXhairLog.log"):
            with open(".AppData/CrossXhairLog.log", 'w') as fichier:
                fichier.close()

        with open(".AppData/Data.json", 'r', encoding="utf-8") as fichier:
            data = json.load(fichier)
            if LastGithubRelease() != data["Info"]["Maj"] :
                reponse = messagebox.askyesno("Question", "An update is available, do you want to download it ?")
                if reponse:
                    Mise_a_jour()

        # Instance partagée
        shared_data = SharedData()

        vérification_thread = threading.Thread(target=vérification, args=(shared_data,))
        vérification_thread2 = threading.Thread(target=vérification2, args=(shared_data,))
        Launcicon = threading.Thread(target=launch_icon)

        vérification_thread.start()
        vérification_thread2.start()
        Launcicon.start()

        try :
            app = QApplication(sys.argv)
            crossair = PyQt_Crosshair.TransparentApp(shared_data)
            crossair.show()
            sys.exit(app.exec())
        except Exeption as e:
            with open(".AppData/CrossXhairLog.log", 'a') as fichier:
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                fichier.write(f"\n[{formatted_time}]:{e}")
    except Exception as e:
        with open(".AppData/CrossXhairLog.log", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:{e}")