from .models import FilamentInventory, ResinInventory

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