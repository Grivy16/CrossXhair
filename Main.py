import sys
import threading
from PyQt6.QtCore import Qt, QCoreApplication, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from tkinter import filedialog
from datetime import datetime
import subprocess
import win32gui
import win32process
import time
import psutil
from pystray import Icon, MenuItem, Menu
import winshell
from tkinter import messagebox
import win32api
import win32con

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

# Application PyQt
class TransparentApp(QWidget):
    def __init__(self, shared_data):
        super().__init__()
        self.shared_data = shared_data  # Référence à l'instance partagée

        # Connexion du signal pour mettre à jour l'image et la taille
        self.shared_data.image_changed.connect(self.update_image)
        self.shared_data.image_size_changed.connect(self.update_image_size)
        self.shared_data.visibility_changed.connect(self.set_visibility)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Centrer la fenêtre
        screen = QApplication.primaryScreen().geometry()
        width, height = 1000, 1000
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

        # Label pour l'image
        self.label = QLabel(self)
        try :
            self.update_image(self.shared_data.Chemin_image)  # Mise à jour initiale de l'image
        except Exception as e :
            with open(".AppData/log.txt", 'a') as fichier:
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                fichier.write(f"\n[{formatted_time}]:{e} | Image not found it deplace or deleted")
            self.update_image(".AppData/Basique.png")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(0, 0, width, height)
        self.label.hide()

    def update_image(self, image_path):
        # Mettre à jour l'image
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(self.shared_data.image_size, self.shared_data.image_size, Qt.AspectRatioMode.KeepAspectRatio)
        self.label.setPixmap(pixmap)

    def update_image_size(self, new_size):
        # Mettre à jour la taille de l'image
        pixmap = QPixmap(self.shared_data.Chemin_image)
        pixmap = pixmap.scaled(new_size, new_size, Qt.AspectRatioMode.KeepAspectRatio)
        self.label.setPixmap(pixmap)
    def set_visibility(self, state):
        """Affiche ou cache l'image selon l'état ('on' ou 'off')"""
        if state == "on":
            self.label.show()  # Affiche l'image
        elif state == "off":
            self.label.hide()  # Cache l'image

# Application CustomTkinter
class Setting(ctk.CTk):
    def __init__(self, shared_data):
        super().__init__()
        self.shared_data = shared_data
        self.title("Settings")
        self.resizable(False, False)
        self.title("Simple Crosshair")
        # Configuration du style

        self.iconbitmap('.AppData/logo.ico')
        self.widget()
        self._keep_on_top()
        self.attributes('-alpha',1)

    def _keep_on_top(self):
        """Maintient la fenêtre en premier plan"""
        self.after(1000, self._keep_on_top)
        self.lift()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
    def change_image(self, img_path):
        with open(".AppData/Data.txt", 'w') as fichier:
            fichier.write(img_path)

            # Créer un CTkImage au lieu de passer le chemin
        try :
            self.preview_image = ctk.CTkImage(
                light_image=Image.open(img_path),
                dark_image=Image.open(img_path),
                size=(150, 150)
            )
        except Exception as e :
            with open(".AppData/log.txt", 'a') as fichier:
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                fichier.write(f"\n[{formatted_time}]:{e} | Image not found it deplace or deleted")
            self.preview_image = ctk.CTkImage(
                light_image=Image.open(".AppData/Basique.png"),
                dark_image=Image.open(".AppData/Basique.png"),
                size=(150, 150)
            )

        # Utiliser l'objet image, pas le chemin
        self.preview_image_label.configure(image=self.preview_image)
        self.preview_title.configure(text=os.path.splitext(os.path.basename(img_path))[0])

    def widget(self):
        self.grid_rowconfigure(3, weight=1)

        ctk.set_appearance_mode("dark")  # Ou "light" selon votre préférence
        ctk.set_default_color_theme("blue")  # Essayez aussi "green" ou "dark-blue"
        self.allowd_frame = ctk.CTkFrame(master=self, width=400, height=40, corner_radius=20)
        self.allowd_frame.grid(row=1, column=0, pady=(10, 5), padx=10)
        self.allowd_frame.grid_propagate(False)
        self.allowd_frame_widget()

        self.preview_frame = ctk.CTkFrame(master=self, width=400, height=200, corner_radius=20)
        self.preview_frame.grid(row=2, column=0, pady=(5, 5), padx=10)
        self.preview_frame.grid_propagate(False)
        self.preview_frame_widget()

        self.catalogue_frame = ctk.CTkScrollableFrame(self, width=365, height=400, corner_radius=20,scrollbar_button_color="#d37000", scrollbar_button_hover_color="#8c5600")
        self.catalogue_frame.grid(row=3, column=0, pady=(5,5), padx=10)
        threading.Thread(target=self.catalogue_frame_widget).start()

        self.addApp_frame = ctk.CTkFrame(master=self, width=400, height=40, corner_radius=20)
        self.addApp_frame.grid(row=1, column=1, pady=(10,5), padx=10)
        self.addApp_frame.grid_propagate(False)
        self.addApp_frame_widget()

        self.appcatalogue_frame = ctk.CTkScrollableFrame(self, width=365, height=400, corner_radius=20,scrollbar_button_color="#d37000", scrollbar_button_hover_color="#8c5600")
        self.appcatalogue_frame.grid(row=2, column=1, pady=(5,5), padx=10, rowspan=2, sticky="n")
        threading.Thread(target=self.appcatalogue_frame_widget).start()

        self.Other_frame = ctk.CTkFrame(master=self, width=400, height=40, corner_radius=20)
        self.Other_frame.grid(row=3, column=1, pady=(245,5), padx=10, sticky="n")
        self.Other_frame.pack_propagate(False)
        self.Other_frame_widget()

    def Other_frame_widget(self):
        self.allowd_frame.grid_rowconfigure(0, weight=1)
        self.allowd_frame.grid_columnconfigure(0, weight=1)
        self.allowd_frame.grid_columnconfigure(1, weight=1)

        self.Start_label = ctk.CTkLabel(self.Other_frame, text="Start with windows", fg_color="transparent", font=("Calibri", 18, "bold"))
        self.Start_label.pack(side="left", pady=10, padx=20)

        self.Start_switch_var = ctk.StringVar(value="off")
        self.Start_switch = ctk.CTkSwitch(
            self.Other_frame,
            text="",
            variable=self.Start_switch_var,
            command=self.Start_switch_event,
            onvalue="on",
            offvalue="off",
            progress_color="#d37000"
        )
        self.Start_switch.pack(side="right", pady=10, padx=20)

    def Start_switch_event(self):
        state = self.Start_switch_var.get()
        if state =="off":
            self.remove_from_startup()
        elif state == "on" :
            self.add_to_startup()

    def add_to_startup(self):
        try:
            link_path = os.path.join(os.getenv('appdata'), r'Microsoft\Windows\Start Menu\Programs\Startup\AutoRunScript.lnk')
            link_target = sys.executable  # Programme en cours d'exécution

            # Création du raccourci
            with winshell.shortcut(link_path) as link:
                link.path = link_target  # Chemin du programme
            messagebox.showinfo("Information","✅ Shortcut added to windows startup.")

        except PermissionError:
            messagebox.showerror("Error",f"🚫 Permission denied: Run the script as administrator. : {e}")
        except Exception as e:
            messagebox.showerror("Error",f"🚫 Error adding shortcut to windows startup : {e}")

    def remove_from_startup(self):
        try:
            # Chemin automatique du dossier de démarrage
            link_path = os.path.join(os.getenv('appdata'), r'Microsoft\Windows\Start Menu\Programs\Startup\AutoRunScript.lnk')

            if os.path.exists(link_path):  # Vérifie si le raccourci existe
                os.remove(link_path)  # Supprime le raccourci
                messagebox.showinfo("Information","✅ Shortcut removed from windows startup")
            else:
                messagebox.showerror("Error",f"🚫 The shortcut does not exist in the startup folder.")

        except Exception as e:
            messagebox.showerror("Error",f"🚫 Error deleting shortcut: {e}")
    def addfilewisget(self):
        self.chemin_files = filedialog.askopenfilename(
            title="Sélectionner un fichier",
            filetypes=[("Fichiers exexutable", "*.exe")]
        )
        with open(".AppData/files.txt", "a", encoding="utf-8") as fichier:
            fichier.write(f"{self.chemin_files}\n")

        for widget in self.appcatalogue_frame.winfo_children():
            widget.destroy()

        # Reconstruire le frame
        self.appcatalogue_frame_widget()

    def addApp_frame_widget(self):
        self.addapp_button = ctk.CTkButton(self.addApp_frame, text="Add Application", width=380, corner_radius=20, font=("Calibri", 18, "bold"),
                                           fg_color="#d37000",
                                           hover_color="#8c5600",
                                           command=self.addfilewisget)
        self.addapp_button.grid(row=0, column=0, padx=10, pady=(6,0))
    def crossair_switch_event(self):
        state = self.crossair_switch_var.get()
        self.shared_data.visibility_changed.emit(state)  # Émet le signal
    def delete_file_function(self, path):
        self.path = path
        with open(".AppData/files.txt", 'r') as fichier:
            contenu = fichier.read()

        contenu_modifié = contenu.replace(path + "\n", "").replace(path, "")

        with open(".AppData/files.txt", 'w') as fichier:
            fichier.write(contenu_modifié)

        # Effacer tous les widgets du frame avant de le reconstruire
        for widget in self.appcatalogue_frame.winfo_children():
            widget.destroy()

        # Reconstruire le frame
        self.appcatalogue_frame_widget()
    def appcatalogue_frame_widget(self):
        with open(".AppData/files.txt", 'r') as fichier:
            lignes = fichier.read().splitlines()
        self.a=0
        for ligne in lignes :
            if ligne :
                self.file_button = ctk.CTkButton(
                    self.appcatalogue_frame,
                    textvariable=ligne,
                    text=os.path.splitext(os.path.basename(ligne))[0],
                    width=300,
                    corner_radius=20,
                    font=("Calibri", 18, "bold"),
                    fg_color="transparent",
                    hover_color="#404040",
                    command=lambda path=ligne:threading.Thread(target=subprocess.run([path]).start())
                    ).grid(row=self.a, column=0, padx=0, pady=10)
                self.delete_file_button = ctk.CTkButton(
                    self.appcatalogue_frame,
                    text="X",
                    width=30,
                    corner_radius=20,
                    font=("Calibri", 20, "bold"),
                    fg_color="red",
                    hover_color="#980000",
                    command=lambda path=ligne:threading.Thread(target=self.delete_file_function(path)).start()
                    ).grid(row=self.a, column=1, padx=(10,0), pady=10)
                self.a+=1
    def allowd_frame_widget(self):
        self.allowd_frame.grid_rowconfigure(0, weight=1)
        self.allowd_frame.grid_columnconfigure(0, weight=1)
        self.allowd_frame.grid_columnconfigure(1, weight=1)

        self.Onoff_label = ctk.CTkLabel(self.allowd_frame, text="enable / disable", fg_color="transparent", font=("Calibri", 18, "bold"))
        self.Onoff_label.grid(row=0, column=0, pady=10, padx=20, sticky="w")

        self.crossair_switch_var = ctk.StringVar(value="off")
        self.crossair_switch = ctk.CTkSwitch(
            self.allowd_frame,
            text="",
            variable=self.crossair_switch_var,
            command=self.crossair_switch_event,
            onvalue="on",
            offvalue="off",
            progress_color="#d37000"
        )
        self.crossair_switch.grid(row=0, column=2, pady=10, padx=20, sticky="e")
    def crossair_switch_event(self):
        state = self.crossair_switch_var.get()
        self.shared_data.visibility_changed.emit(state)  # Émet le signal

    def preview_frame_widget(self):
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(1, weight=1)
        try :
            self.preview_image = ctk.CTkImage(
                light_image=Image.open(self.shared_data.Chemin_image),
                dark_image=Image.open(self.shared_data.Chemin_image),
                size=(150, 150)
            )
        except Exception as e :
            with open(".AppData/log.txt", 'a') as fichier:
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                fichier.write(f"\n[{formatted_time}]:{e} | Image not found it deplace or deleted")
            self.preview_image = ctk.CTkImage(
                light_image=Image.open(".AppData/Basique.png"),
                dark_image=Image.open(".AppData/Basique.png"),
                size=(150, 150)
            )

        self.preview_image_label = ctk.CTkLabel(self.preview_frame, image=self.preview_image, text="", fg_color="transparent")
        self.preview_image_label.grid(row=0, column=0, pady=10, padx=10, rowspan=3, sticky="nsew")

        self.preview_title = ctk.CTkLabel(self.preview_frame, text=os.path.splitext(os.path.basename(self.shared_data.Chemin_image))[0], fg_color="transparent", font=("Calibri", 25, "bold"))
        self.preview_title.grid(row=0, column=1, pady=0, padx=10)

        self.open_button = ctk.CTkButton(
            self.preview_frame, text="Open ",
            width=200,
            font=("Calibri", 18, "bold"),
            fg_color='gray',
            hover_color="#404040",
            command=self.chose_file_image,
            corner_radius=20
        )

        self.open_button.grid(row=1, column=1, pady=0, padx=10)
        self.apply_button = ctk.CTkButton(
            self.preview_frame,
            text="Apply",
            width=200,
            font=("Calibri", 18, "bold"),
            command=self.apply_image,  # Utilisation correcte de la fonction
            corner_radius=20,
            fg_color="#d37000",
            hover_color="#8c5600"
        )
        self.apply_button.grid(row=2, column=1, pady=(20,20), padx=10)

        def slider_event(value):
            self.shared_data.set_image_size(int(value))

        self.size_slider = ctk.CTkSlider(self.preview_frame, from_=10, to=400, command=slider_event, width=400, button_color="#d37000", button_hover_color="#8c5600")
        self.size_slider.grid(row=4, column=0, pady=10, padx=10, columnspan=2)

    def catalogue_frame_widget(self):
        images = []
        for file in os.listdir(".AppData"):
            if file.endswith(".png"):
                images.append(os.path.join(".AppData", file))

        grid_row = 0
        grid_column = 0

        for img_path in images:
            img_tk = ctk.CTkImage(
                light_image=Image.open(img_path),
                dark_image=Image.open(img_path),
                size=(65, 65)
            )
            # Créer un bouton avec l'image
            button = ctk.CTkButton(
                self.catalogue_frame,
                image=img_tk,
                text="",
                width=65,
                height=70,
                fg_color="transparent",
                hover_color="#404040",
                command=lambda p=img_path: self.change_image(p),
                corner_radius=20,
                border_width=2,
            )
            button.grid(row=grid_row, column=grid_column, padx=5, pady=5,ipady=10)

            # Mettre à jour les indices du cadrillage
            grid_column += 1
            if grid_column > 2:  # Passer à la ligne suivante après 4 colonnes
                grid_column = 0
                grid_row += 1

            # Empêcher le garbage collector de détruire l'image
            button.image = img_tk

    def chose_file_image(self):
        self.chemin_fichier = filedialog.askopenfilename(
            title="Sélectionner un fichier",
            filetypes=[("Fichiers d'image", "*.png"), ("Fichiers d'image", "*.jpeg"), ("Fichiers d'image", "*.jpg"), ("Fichiers d'image", "*.webp"), ("Fichiers d'animation", "*.gif"), ("Tous les fichiers", "*.*")]
        )
        with open(".AppData/Data.txt", 'w') as fichier:
            fichier.write(self.chemin_fichier)
        self.preview_image = ctk.CTkImage(
            light_image=Image.open(self.chemin_fichier),
            dark_image=Image.open(self.chemin_fichier),
            size=(150, 150)
        )
        self.preview_image_label.configure(image=self.preview_image)

        self.preview_title.configure(text=os.path.splitext(os.path.basename(self.chemin_fichier))[0])

    def apply_image(self):
        # Appliquer le nouveau chemin d'image
        with open(".AppData/Data.txt", 'r') as fichier:
            self.chemin_fichier = fichier.read()
        self.shared_data.set_image(self.chemin_fichier)

def run_pyqt_app(shared_data):
    pass

def run_customtkinter_app(shared_data):
    try :
        app = Setting(shared_data)
        app.attributes('-alpha',1)
        app.mainloop()
    except Exception as e:
        with open(".AppData/log.txt", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:{e}")
        if "No such file or directory" in str(e):
            with open(".AppData/data.txt", 'w') as fichier:
                fichier.write(".AppData/Basique.png")
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
    icon = Icon("test_icon", Image.open('.AppData/logo.ico'), menu=Menu(
                    MenuItem("Paramètre", launchsetting),
                    MenuItem("Quitter", quittéicon),
                ))
    icon.run()

if __name__ == "__main__":
    try :
        os.makedirs(".AppData", exist_ok=True)

        if not os.path.exists(".AppData/Data.txt"):
            with open(".AppData/Data.txt", 'w') as fichier:
                fichier.write(".AppData/Basique.png")
        if not os.path.exists(".AppData/log.txt"):
            with open(".AppData/log.txt", 'w') as fichier:
                fichier.close()
        if not os.path.exists(".AppData/files.txt"):
            with open(".AppData/files.txt", 'w') as fichier:
                fichier.close()

        # Instance partagée
        shared_data = SharedData()

        # Créer des threads pour exécuter les deux applications
        #pyqt_thread = threading.Thread(target=run_pyqt_app, args=(shared_data,))

        vérification_thread = threading.Thread(target=vérification, args=(shared_data,))
        Launcicon = threading.Thread(target=launch_icon)

        # Démarrer les deux threads
        #pyqt_thread.start()

        vérification_thread.start()
        Launcicon.start()

        try :
            app = QApplication(sys.argv)
            crossair = TransparentApp(shared_data)
            crossair.show()
            sys.exit(app.exec())
        except Exeption as e:
            with open(".AppData/log.txt", 'a') as fichier:
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                fichier.write(f"\n[{formatted_time}]:{e}")
        # Attendre la fin des threads
        #pyqt_thread.join()
        customtkinter_thread.join()
    except Exception as e:
        with open(".AppData/log.txt", 'a') as fichier:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            fichier.write(f"\n[{formatted_time}]:{e}")