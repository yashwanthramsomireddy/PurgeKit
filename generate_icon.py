"""
PurgeKit — Icon Generator
Run this once before building to create assets/icon.ico
"""
import os
from PIL import Image, ImageDraw

def generate_icon(accent_color=(0, 230, 118)):
    size = 256
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r, g, b = accent_color
    draw.ellipse([4,4,252,252], fill=(10,10,10,255), outline=(r,g,b,255), width=6)
    draw.ellipse([20,20,236,236], outline=(r,g,b,80), width=2)
    draw.line([(128,60),(128,160)], fill=(r,g,b), width=10)
    for i, offset in enumerate([-40,-25,-10,5,20,35,50]):
        draw.line([(128,160),(88+offset,210)],
                  fill=(r,g,b,max(60,255-i*28)), width=5)
    draw.ellipse([118,50,138,70], fill=(r,g,b,255))
    return img

os.makedirs("assets", exist_ok=True)
img = generate_icon((0, 230, 118))
img.save("assets/icon.ico", format="ICO",
         sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
print("✅ assets/icon.ico created")
