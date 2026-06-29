from PIL import Image

# Buka logo Anda (ganti 'logo_saya.png' dengan nama file Anda)
img = Image.open('icon.png')

# Resize ke ukuran yang bagus (opsional, jika logo terlalu besar)
img = img.resize((256, 256), Image.LANCZOS)

# Simpan sebagai PNG (untuk window icon)
img.save('icon.png')
print("✅ icon.png berhasil dibuat")

# Simpan sebagai ICO (untuk EXE icon)
img.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
print("✅ icon.ico berhasil dibuat")

print("\n📁 Kedua file sudah sama! Silakan compile ulang.")