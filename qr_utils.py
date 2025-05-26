import qrcode

def generate_qr_text(type, material, color, diameter_mm, control_number):
    prefix = "F-" if type.lower() == "filament" else "R-"
    if type.lower() == "filament":
        diameter_code = 'A' if diameter_mm == 1.75 else 'B'
        return f"{prefix}{material}{color}{diameter_code}{control_number:02d}"
    else:
        return f"{prefix}{material}{color}{control_number:02d}"

def generate_qr_image(qr_text, path):
    img = qrcode.make(qr_text)
    img.save(path)
