import subprocess
import platform
import time

chemin_fichier = "player.py"

# Vérifiez le système d'exploitation


def lancer_arriere_plan(chemin_fichier, comment="--"):
    syst_exploitation = platform.system()
    try:
        if syst_exploitation == "Windows":
            subprocess.run(["start", "cmd", "/c", "python", chemin_fichier])
        elif syst_exploitation == "Linux":
            subprocess.run(["gnome-terminal", "--", "python", chemin_fichier])
        elif syst_exploitation == "Darwin":  # macOS
            subprocess.run(["open", "-a", "Terminal", "python", chemin_fichier])
        else:
            print("Système d'exploitation non pris en charge.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script : {e}")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")

def lancer_premier_plan(chemin_fichier, comment="--"):
    syst_exploitation = platform.system()
    try:
        if syst_exploitation == "Windows":
            subprocess.run(["start", "cmd", "/c", "python", chemin_fichier], check=True)
        elif syst_exploitation == "Linux":
            subprocess.run(["gnome-terminal", "--", "python", chemin_fichier], check=True)
        elif syst_exploitation == "Darwin":  # macOS
            subprocess.run(["open", "-a", "Terminal", "python", chemin_fichier], check=True)
        else:
            print("Système d'exploitation non pris en charge.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script : {e}")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")

fichier1 = "player.py"
fichier2= "game.py"
lancer_arriere_plan(fichier2)

lancer_premier_plan(fichier1, "--full-screen")