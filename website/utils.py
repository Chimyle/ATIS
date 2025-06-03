from .models import FilamentInventory, ResinInventory
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
from .models import db

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
        "Silver": "Sr",
        "Pink": "Pk",
    }
    return color_map.get(color, color[:2].capitalize())

def get_size_code(size):
    return "A" if size == "1.75mm" else "B"

def generate_unique_code(material, color, size):
    color_code = shorten_color(color)
    size_code = get_size_code(size)
    base_code = f"SB{color_code}{size_code}" if material=="SimuBone" else f"{material}{color_code}{size_code}"

    count = FilamentInventory.query.filter(FilamentInventory.code.like(f"{base_code}%")).count()
    control_number = f"{count + 1:02d}"
    return f"{base_code}{control_number}"

def generate_resin_code(material):
    base = material[:3].upper()
    count = ResinInventory.query.count()
    return f"{base}{count + 1:02d}"

def generate_qr_with_label(material_code, save_dir="static/qr_codes", font_size=20):
    os.makedirs(save_dir, exist_ok=True)

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(material_code)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Load TrueType font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)  # Customize path if needed
    except IOError:
        font = ImageFont.load_default()
        print("Could not load TrueType font, using default.")

    # Measure text size
    bbox = font.getbbox(material_code)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Add spacing above and below text
    spacing_above_text = 5
    spacing_below_text = 15  # More space for cutting room

    # Create new image with space for label
    qr_width, qr_height = img_qr.size
    total_height = qr_height + spacing_above_text + text_height + spacing_below_text
    img_with_text = Image.new("RGB", (qr_width, total_height), "white")

    # Paste QR code on new image
    img_with_text.paste(img_qr, (0, 0))

    # Draw text and border
    draw = ImageDraw.Draw(img_with_text)
    text_x = (qr_width - text_width) // 2
    text_y = qr_height + spacing_above_text
    draw.text((text_x, text_y), material_code, font=font, fill="black")

    # Draw rectangle around everything
    draw.rectangle([0, 0, qr_width - 1, total_height - 1], outline="black", width=2)

    # Save
    file_path = os.path.join(save_dir, f"{material_code}.png")
    img_with_text.save(file_path)
    return file_path

def populate_filament_choices(form):
    choices = db.session.query(FilamentInventory.id, FilamentInventory.code).all()
    form.material_code.choices = [(str(item.id), item.code) for item in choices]

def convert_mins(duration_str):
    try:
        hours, minutes = map(int, duration_str.split(':'))
        return hours * 60 + minutes
    except ValueError:
        return None