import json, os, sys, textwrap, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageOps

run_id = sys.argv[1]
urls = json.loads(sys.argv[2])
judul = sys.argv[3].strip().upper() if len(sys.argv) > 3 and sys.argv[3].strip() else "DOKUMENTASI KEGIATAN"
template_url = "https://drive.google.com/uc?export=download&id=10qmOVChIqW9CHSfBJXrnQX5U9v-Cb4hf"

W, H = 1080, 1350
GAP = 12              # Lebar garis pemisah antar foto (px)
BG_COLOR = (255, 255, 255)  # Warna garis pemisah (Putih)
TITLE_Y = 120         # Posisi Y kotak judul (geser angka ini jika menabrak logo template)

def download_img(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        from io import BytesIO
        return Image.open(BytesIO(resp.read()))

# 1. Download semua foto (2-6 foto)
photos = [download_img(u).convert("RGB") for u in urls[:6]]
n = len(photos)

# 2. Tentukan layout grid cerdas (x, y, width, height)
canvas = Image.new("RGB", (W, H), BG_COLOR)
g = GAP

if n == 2:
    h2 = (H - g) // 2
    boxes = [(0, 0, W, h2), (0, h2 + g, W, H - h2 - g)]
elif n == 3:
    h2 = (H - g) // 2
    w2 = (W - g) // 2
    boxes = [
        (0, 0, W, h2),
        (0, h2 + g, w2, H - h2 - g),
        (w2 + g, h2 + g, W - w2 - g, H - h2 - g),
    ]
elif n == 4:
    h2 = (H - g) // 2
    w2 = (W - g) // 2
    boxes = [
        (0, 0, w2, h2), (w2 + g, 0, W - w2 - g, h2),
        (0, h2 + g, w2, H - h2 - g), (w2 + g, h2 + g, W - w2 - g, H - h2 - g),
    ]
elif n == 5:
    h2 = (H - g) // 2
    w2 = (W - g) // 2
    w3 = (W - 2 * g) // 3
    boxes = [
        (0, 0, w2, h2), (w2 + g, 0, W - w2 - g, h2),
        (0, h2 + g, w3, H - h2 - g),
        (w3 + g, h2 + g, w3, H - h2 - g),
        (2 * (w3 + g), h2 + g, W - 2 * (w3 + g), H - h2 - g),
    ]
else:  # 6 foto (Grid 2x3)
    h3 = (H - 2 * g) // 3
    w2 = (W - g) // 2
    boxes = []
    for r in range(3):
        y = r * (h3 + g)
        bh = h3 if r < 2 else H - y
        boxes.append((0, y, w2, bh))
        boxes.append((w2 + g, y, W - w2 - g, bh))

# 3. Center-crop & tempel foto ke kanvas
for img, (x, y, bw, bh) in zip(photos, boxes):
    fitted = ImageOps.fit(img, (bw, bh), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    canvas.paste(fitted, (x, y))

# 4. Tempel Template Overlay PNG
canvas = canvas.convert("RGBA")
try:
    overlay = download_img(template_url).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    canvas = Image.alpha_composite(canvas, overlay)
except Exception as e:
    print("Warning overlay:", e)

# 5. Gambar Banner Judul Kegiatan di Bagian Atas
draw = ImageDraw.Draw(canvas)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font = ImageFont.truetype(font_path, 40) if os.path.exists(font_path) else ImageFont.load_default()

lines = textwrap.wrap(judul, width=30)[:2]  # Maksimal 2 baris agar rapi
line_h = 52
pad_y = 22
box_h = len(lines) * line_h + pad_y * 2
margin_x = 50

# Kotak semi-transparan gelap dengan sudut melengkung
draw.rounded_rectangle(
    [(margin_x, TITLE_Y), (W - margin_x, TITLE_Y + box_h)],
    radius=18,
    fill=(15, 23, 42, 215),
    outline=(255, 255, 255, 180),
    width=3
)

for idx, line in enumerate(lines):
    bbox = draw.textbbox((0, 0), line, font=font)
    tw = bbox[2] - bbox[0]
    tx = (W - tw) // 2
    ty = TITLE_Y + pad_y + idx * line_h
    draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 255))

canvas.convert("RGB").save(f"kolase_{run_id}.jpg", "JPEG", quality=95)
print(f"Saved kolase_{run_id}.jpg")
