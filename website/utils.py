from .models import FilamentInventory, ResinInventory
from io import BytesIO
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
from .models import db, FilamentInventory, ResinInventory
import pandas as pd
from datetime import datetime

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
        "Fire Engine Red": "FERD",
        "Transparent": "Tt",
        "Light Gray": "LGy",
        "Dark Gray": "DGy",
        "Cold White": "CWe",
    }
    return color_map.get(color, color[:2].capitalize())

def get_size_code(size):
    return "A" if size == "1.75mm" else "B"

def generate_unique_code(material, color, size):
    color_code = shorten_color(color)
    size_code = get_size_code(size)
    if material == "ePLA+HS":
        base_code = f"PLA+{color_code}{size_code}"
    elif material == "SimuBone":
        base_code = f"SB{color_code}{size_code}"
    elif material == "Nylon":
        base_code = f"Nyl{color_code}{size_code}"
    elif material == "PolyDissolve":
        base_code = f"PD{color_code}{size_code}"
    elif material == "PolyFlex TPU 95" or material == "Ultimaker TPU":
        base_code = f"TPU{color_code}{size_code}"
    elif material == "Polylite PLA" or material == "PolyTerra PLA":
        base_code = f"PLA{color_code}{size_code}"
    elif material == "Thermax PEEK":
        base_code = f"PEEK{color_code}{size_code}"
    elif material == "Tough PLA":
        base_code = f"TPLA{color_code}{size_code}"
    else:
        base_code = f"{material}{color_code}{size_code}"


    count = FilamentInventory.query.filter(FilamentInventory.code.like(f"{base_code}%")).count()
    control_number = f"{count + 1:02d}"
    return f"{base_code}{control_number}"

def generate_resin_code(material):
    base = material[:2].upper()
    count = ResinInventory.query.filter(ResinInventory.material_code.like(f"{base}%")).count()
    return f"{base}{count + 1:02d}"

def generate_qr_with_label(material_code, font_size=20):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(material_code)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Measure text
    bbox = font.getbbox(material_code)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Layout sizes
    spacing_above_text = 5
    spacing_below_text = 15
    qr_width, qr_height = img_qr.size
    total_height = qr_height + spacing_above_text + text_height + spacing_below_text

    # Create image
    img_with_text = Image.new("RGB", (qr_width, total_height), "white")
    img_with_text.paste(img_qr, (0, 0))

    # Draw text and border
    draw = ImageDraw.Draw(img_with_text)
    text_x = (qr_width - text_width) // 2
    text_y = qr_height + spacing_above_text
    draw.text((text_x, text_y), material_code, font=font, fill="black")
    draw.rectangle([0, 0, qr_width - 1, total_height - 1], outline="black", width=2)

    # Save to memory
    img_io = BytesIO()
    img_with_text.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

def populate_filament_choices(form):
    choices = db.session.query(FilamentInventory.id, FilamentInventory.code).all()
    form.material_code.choices = [(str(item.id), item.code) for item in choices]

def convert_mins(duration_str):
    try:
        hours, minutes = map(int, duration_str.split(':'))
        return hours * 60 + minutes
    except ValueError:
        return None
def update_choices(field, items):
    existing = {v for v, _ in field.choices}
    field.choices += [(i, i) for i in items if i not in existing]
    if "__new__" not in existing:
        field.choices.append(("__new__", "Add New"))
def import_filaments_from_excel(file_path):
    df = pd.read_excel(file_path, sheet_name="Filaments", header=1)

    for _, row in df.iterrows():
        status = str(row.get("status") or row.get("Status") or "").strip().lower()
        if status == "consumed":
            continue 
        code = str(row.get("Item ID")).strip()
        if not code or FilamentInventory.query.filter_by(code=code).first():
            continue  # skip if code missing or already exists

        material = str(row.get("Material")).strip()
        color = str(row.get("Color")).strip()
        size = str(row.get("Diameter")).strip()
        location = str(row.get("Location")).strip() if pd.notna(row.get("Location")) else "Shelf"

        filament = FilamentInventory(
            code=code,
            material=material,
            color=color,
            size=size,
            weight_remaining=1000.0,
            location=location
        )
        db.session.add(filament)
    
    db.session.commit()


def import_resins_from_excel(file_path):
    df = pd.read_excel(file_path, sheet_name="Resins", header=1)

    for _, row in df.iterrows():
        status = str(row.get("status") or row.get("Status") or "").strip().lower()
        if status == "consumed":
            continue 

        material_code = str(row.get("Stock ID")).strip()
        if not material_code or ResinInventory.query.filter_by(material_code=material_code).first():
            continue  # skip if missing or exists

        def parse_date(val):
            if pd.isna(val):
                return None
            if isinstance(val, datetime):
                return val.date()
            try:
                return pd.to_datetime(val).date()
            except Exception:
                return None

        resin = ResinInventory(
            material=str(row.get("Material")).strip(),
            material_code=material_code,
            printer=str(row.get("Printer")).strip(),
            date_mfg=parse_date(row.get("Date of Mfg")),
            date_expiry=parse_date(row.get("Date of Expiry")),
            date_delivered=parse_date(row.get("Date Delivered")),
            date_opened=parse_date(row.get("Date Opened")),
            status=str(row.get("status")).strip() if pd.notna(row.get("status")) else None,
            location="Shelf"
        )
        db.session.add(resin)
    
    db.session.commit()