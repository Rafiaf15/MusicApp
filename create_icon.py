from PIL import Image, ImageDraw, ImageFont
import os

def create_music_icon():
    """Buat icon aplikasi music player"""
    # Buat image 512x512
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background gradient (lingkaran)
    # Warna Spotify green
    green = (29, 185, 84)
    
    # Gambar lingkaran dengan gradient effect
    for i in range(size//2, 0, -1):
        # Gradient dari gelap ke terang
        factor = i / (size//2)
        r = int(green[0] * (1 - factor * 0.3))
        g = int(green[1] * (1 - factor * 0.2))
        b = int(green[2] * (1 - factor * 0.3))
        draw.ellipse(
            [size//2 - i, size//2 - i, size//2 + i, size//2 + i],
            fill=(r, g, b)
        )
    
    # Gambar note musik (🎵) dengan bentuk sederhana
    # Note 1 (kiri)
    draw.ellipse([170, 320, 230, 380], fill='white')  # Kepala note
    draw.rectangle([225, 150, 235, 340], fill='white')  # Tangkai
    draw.arc([225, 120, 310, 200], 0, 180, fill='white', width=10)  # Bendera
    
    # Note 2 (kanan)
    draw.ellipse([280, 290, 340, 350], fill='white')  # Kepala note
    draw.rectangle([335, 120, 345, 310], fill='white')  # Tangkai
    
    # Garis penghubung
    draw.rectangle([225, 120, 345, 135], fill='white')
    
    # Save PNG
    img.save('icon.png')
    print("✅ icon.png berhasil dibuat!")
    
    # Convert ke ICO untuk Windows
    img.save('icon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("✅ icon.ico berhasil dibuat!")

if __name__ == "__main__":
    create_music_icon()