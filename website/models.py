from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    material = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(5), nullable=False)
    weight_remaining = db.Column(db.Float, nullable=False)
    qr_filename = db.Column(db.String(100))
    location = db.Column(db.String(100))

class PrintLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_started = db.Column(db.Date, default=datetime.today)
    time_started = db.Column(db.Time, default=datetime.now().time)
    model_name = db.Column(db.String(100))
    printer_name = db.Column(db.String(50))
    material_code = db.Column(db.String(20))
    material_used = db.Column(db.Float)
    duration = db.Column(db.Integer)
    layer_height = db.Column(db.Float)
    nozzle_temp = db.Column(db.Integer)
    bed_temp = db.Column(db.Integer)
    chamber_temp = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(10), default="Active")
    time_claimed = db.Column(db.Time, nullable=True)
