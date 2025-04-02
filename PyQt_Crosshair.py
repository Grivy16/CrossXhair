from PyQt6.QtCore import Qt, QCoreApplication, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *

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
            self.update_image("Image/Basique.png")
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