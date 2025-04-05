# updater.py
import os
import sys
import time
import shutil
import psutil
import subprocess

def wait_until_process_ends(name):
    while True:
        found = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == name:
                found = True
                break
        if not found:
            break
        time.sleep(0.5)

def main():
    temp_file = "Main_temp.exe"
    target_file = "CrossXhair.exe"
    time.sleep(3)


    try:
        if os.path.exists(target_file):
            os.remove(target_file)
        shutil.move(temp_file, target_file)
        print("Mise à jour effectuée.")

        # Relancer l'application
        subprocess.Popen([target_file], shell=True)
        sys.exit()
    except Exception as e:
        print(f"Erreur durant la mise à jour : {e}")
        time.sleep(5)
        sys.exit()

def launch() :
    main()

if __name__ == "__main__":
    launch()