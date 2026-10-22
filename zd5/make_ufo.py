from PIL import Image, ImageDraw

# Создаём картинку 100×100 с прозрачным фоном
img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Нижняя тарелка (эллипс)
draw.ellipse([5, 45, 95, 75], fill=(160, 160, 160, 255), outline=(50, 50, 50, 255))

# Купол (эллипс сверху)
draw.ellipse([30, 25, 70, 55], fill=(120, 220, 255, 230), outline=(50, 50, 50, 255))

# Огни (маленькие жёлтые кружки снизу)
for x in [20, 35, 50, 65, 80]:
    draw.ellipse([x, 58, x + 6, 64], fill=(255, 255, 0, 255), outline=(200, 150, 0, 255))

img.save("ufo.png")
print("Создан ufo.png")