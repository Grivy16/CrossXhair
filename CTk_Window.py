import sys
import threading
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from tkinter import filedialog, messagebox
from datetime import datetime
import subprocess
from pathlib import Path

class Setting(ctk.CTk):
    def __init__(self, shared_data):
        super().__init__()
        self.shared_data = shared_data
        self.resizable(False, False)
        self.title("CrossXhair Setting")
        self.iconbitmap('.AppData/logo.ico')
        self.widget()
        self.minsize(460, 780)
        self.maxsize(2000, 780)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


        #self.bind("<Map>", self.on_restore)  # Se déclenche quand la fenêtre est restaurée

    def on_closing(self):
        self.destroy()
        self.quit()

    def widget(self):
        self.tabview = ctk.CTkTabview(self, fg_color="transparent", segmented_button_selected_color ="#d37000", segmented_button_selected_hover_color="#d37000", corner_radius=20)
        self.tabview.pack()

        self.tabview.add("Setting")  # add tab at the end
        self.tabview.add("Advanced Setting")  # add tab at the end
        self.tabview.set("Setting")  # set currently visible tab

        ctk.set_appearance_mode("dark")  # Ou "light" selon votre préférence
        ctk.set_default_color_theme("blue")  # Essayez aussi "green" ou "dark-blue"
        self.allowd_frame = ctk.CTkFrame(master=self.tabview.tab("Setting"), width=400, height=40, corner_radius=20)
        self.allowd_frame.grid(row=1, column=0, pady=(10, 5), padx=(0,5))
        self.allowd_frame.grid_propagate(False)
        self.allowd_frame_widget()

        self.preview_frame = ctk.CTkFrame(master=self.tabview.tab("Setting"), width=400, height=200, corner_radius=20)
        self.preview_frame.grid(row=2, column=0, pady=(5, 5), padx=10)
        self.preview_frame.grid_propagate(False)
        self.preview_frame_widget()

        self.catalogue_frame = ctk.CTkScrollableFrame(master=self.tabview.tab("Setting"), width=365, height=400, corner_radius=20,scrollbar_button_color="#d37000", scrollbar_button_hover_color="#8c5600")
        self.catalogue_frame.grid(row=3, column=0, pady=(5,0), padx=10)
        threading.Thread(target=self.catalogue_frame_widget).start()

        self.addApp_frame = ctk.CTkFrame(master=self.tabview.tab("Advanced Setting"), width=400, height=40, corner_radius=20)
        self.addApp_frame.grid(row=0, column=0, pady=(0,5), padx=10)
        self.addApp_frame.grid_propagate(False)
        self.addApp_frame_widget()

        self.appcatalogue_frame = ctk.CTkScrollableFrame(master=self.tabview.tab("Advanced Setting"), width=365, height=400, corner_radius=20,scrollbar_button_color="#d37000", scrollbar_button_hover_color="#8c5600")
        self.appcatalogue_frame.grid(row=1, column=0, pady=(5,5), padx=10)
        threading.Thread(target=self.appcatalogue_frame_widget).start()

        self.Other_frame = ctk.CTkFrame(master=self.tabview.tab("Advanced Setting"), width=400, height=40, corner_radius=20)
        self.Other_frame.grid(row=2, column=0, pady=(5,0), padx=10)
        self.Other_frame.pack_propagate(False)
        self.Other_frame_widget()

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
                light_image=Image.open("Image/Basique.png"),
                dark_image=Image.open("Image/Basique.png"),
                size=(150, 150)
            )

        # Utiliser l'objet image, pas le chemin
        self.preview_image_label.configure(image=self.preview_image)
        self.preview_title.configure(text=os.path.splitext(os.path.basename(img_path))[0])
    def Other_frame_widget(self):
        self.Start_label = ctk.CTkLabel(self.Other_frame, text="Start with windows", fg_color="transparent", font=("Calibri", 18, "bold"))
        self.Start_label.grid(row=0, column=0, pady=(10,5), padx=20)

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
        self.Start_switch.grid(row=0, column=1, pady=(10,5), padx=20)
        self.openfiles_btn = ctk.CTkButton(self.Other_frame, text="Open files", width=380, corner_radius=20, font=("Calibri", 18, "bold"),
                                           fg_color="gray",
                                           hover_color="#404040",
                                           command=lambda : os.startfile(Path.cwd()))
        self.openfiles_btn.grid(row=1, column=0, pady=(5,10), padx=10, columnspan=2)
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
                light_image=Image.open("Image/Basique.png"),
                dark_image=Image.open("Image/Basique.png"),
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
        for file in os.listdir("Image"):
            if file.endswith(".png"):
                images.append(os.path.join("Image", file))

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
            filetypes=[("Fichiers d'image", "*.png"), ("Fichiers d'image", "*.jpeg"), ("Fichiers d'image", "*.jpg"), ("Fichiers d'image", "*.webp"), ("Fichiers d'animation", "*.gif")]
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

