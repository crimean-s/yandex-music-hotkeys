import os
import subprocess
import sys
from PIL import Image

def generate_icon():
    """Generate a temporary icon if none exists, to ensure assets folder is populated."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    icon_path = os.path.join(assets_dir, "icon.ico")

    if not os.path.exists(icon_path):
        print("Generating default icon...")
        size = 256
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        # Draw a circle
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, size, size), fill="#FFCC00")
        # Draw a music note or play symbol (triangle)
        draw.polygon([(80, 60), (80, 196), (200, 128)], fill="black")
        img.save(icon_path, format="ICO")

def main():
    # Ensure icon exists
    generate_icon()

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name", "YandexMusicHotkeys",
        "--add-data", "assets;assets",
        "--icon", "assets/icon.ico",
        "run.py"
    ]

    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\nBuild complete. Check the 'dist' folder.")

if __name__ == "__main__":
    main()
