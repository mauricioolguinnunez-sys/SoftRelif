import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.music_catalog import get_all_music


tracks = get_all_music()

print("Audios detectados:", len(tracks))

for track in tracks:
    print()
    print("ID:", track["id"])
    print("Título:", track["title"])
    print("Categoría:", track["category"])
    print("Ruta:", track["relative_path"])
    print("Modo Calma:", track["calm_mode"])
    print("Background:", track["background_sound"])