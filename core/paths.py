from pathlib import Path
import os

def get_all_worlds():
    user = os.getenv("USERNAME")
    base = Path(f"C:/Users/{user}/Zomboid/Saves")

    if not base.exists():
        raise FileNotFoundError("Project Zomboid save directory not found")

    worlds = []
    for mode in base.iterdir():
        if mode.is_dir():
            for world in mode.iterdir():
                if world.is_dir():
                    worlds.append({
                        "mode": mode.name,
                        "name": world.name,
                        "path": world
                    })

    if not worlds:
        raise FileNotFoundError("No Project Zomboid worlds found")

    return worlds
