from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))  # 'Filament' or 'Resin'
    material = db.Column(db.String(50))
    color = db.Column(db.String(20))
    diameter = db.Column(db.Float, nullable=True)  # Only for filament
    control_number = db.Column(db.Integer)
    location = db.Column(db.String(50))
    quantity = db.Column(db.Float)  # in grams or mL
    qr_code_text = db.Column(db.String(50), unique=True)

class PrinterLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_started = db.Column(db.Date)
    time_started = db.Column(db.Time)
    model_name = db.Column(db.String(100))
    printer_name = db.Column(db.String(50))
    material_id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'))
    amount_used = db.Column(db.Float)
    duration = db.Column(db.String(50))
    layer_height = db.Column(db.Float)
    nozzle_temp = db.Column(db.Integer)
    bed_temp = db.Column(db.Integer)
    chamber_temp = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(10))  # "Pending", "Done", "Fail"
    time_claimed = db.Column(db.DateTime, nullable=True)
