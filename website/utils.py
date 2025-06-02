from .models import FilamentInventory, ResinInventory
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def shorten_color(color):
    color_map = {
        "Black": "Bk",
        "White": "We",
        "Red": "Rd",
        "Blue": "Be",
        "Green": "Gn",
        "Yellow": "Yl",
        "Gray": "Gy",
        "Orange": "Or",
        "Bone White": "BWe",
        "Natural": "Nl",
        "Clear": "Cl",
    }
    return color_map.get(color, color[:2].capitalize())

def get_size_code(size):
    return "A" if size == "1.75mm" else "B"

def generate_unique_code(material, color, size):
    color_code = shorten_color(color)
    size_code = get_size_code(size)
    base_code = f"{material}{color_code}{size_code}"

    count = FilamentInventory.query.filter(FilamentInventory.code.like(f"{base_code}%")).count()
    control_number = f"{count + 1:02d}"
    return f"{base_code}{control_number}"

def generate_resin_code(material):
    base = material[:3].upper()
    count = ResinInventory.query.count()
    return f"{base}{count + 1:02d}"

def generate_qr_with_label(material_code, save_dir="static/qr_codes"):
    os.makedirs(save_dir, exist_ok=True)

    qr = qrcode.QRCode(
        version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10, border=4
    )
    qr.add_data(material_code)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    font = ImageFont.load_default()
    bbox = font.getbbox(material_code)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    width, height = img_qr.size
    total_height = height + text_height + 10
    img_with_text = Image.new("RGB", (width, total_height), "white")
    img_with_text.paste(img_qr, (0, 0))
    draw = ImageDraw.Draw(img_with_text)
    draw.text(((width - text_width) // 2, height + 5), material_code, font=font, fill="black")

    file_path = os.path.join(save_dir, f"{material_code}.png")
    img_with_text.save(file_path)
    return file_path