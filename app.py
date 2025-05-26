from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
import os
import qrcode
from models import db, InventoryItem, PrinterLog

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(basedir, 'qr_codes')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    items = InventoryItem.query.all()
    return render_template('inventory.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        type_ = request.form['type']
        material = request.form['material']
        color = request.form['color']
        diameter_code = request.form['diameter']
        control_number = request.form['control_number']
        location = request.form['location']
        quantity = float(request.form['quantity'])

        diameter = 1.75 if diameter_code == 'A' else 2.85 if diameter_code == 'B' else None
        code = f"{material}{color}{diameter_code}{control_number}"

        new_item = InventoryItem(
            type=type_,
            material=material,
            color=color,
            diameter=diameter,
            control_number=int(control_number),
            location=location,
            quantity=quantity,
            qr_code_text=code
        )

        db.session.add(new_item)
        db.session.commit()

        # Generate QR
        img = qrcode.make(code)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{code}.png")
        img.save(img_path)

        return redirect(url_for('inventory'))

    return render_template('add_item.html')

@app.route('/printer_log')
def printer_log():
    logs = PrinterLog.query.order_by(PrinterLog.date_started.desc()).all()
    return render_template('printer_log.html', logs=logs)

@app.route('/log_print', methods=['GET', 'POST'])
def log_print():
    materials = InventoryItem.query.all()
    if request.method == 'POST':
        log = PrinterLog(
            date_started=date.fromisoformat(request.form['date_started']),
            time_started=time.fromisoformat(request.form['time_started']),
            model_name=request.form['model_name'],
            printer_name=request.form['printer_name'],
            material_id=request.form['material_id'],
            amount_used=float(request.form['amount_used']),
            duration=request.form['duration'],
            layer_height=float(request.form['layer_height']),
            nozzle_temp=int(request.form['nozzle_temp']),
            bed_temp=int(request.form['bed_temp']),
            chamber_temp=int(request.form['chamber_temp']) if request.form['chamber_temp'] else None,
            status="Pending",
            time_claimed=None
        )

        # Subtract material from inventory
        item = InventoryItem.query.get(request.form['material_id'])
        item.quantity -= log.amount_used

        db.session.add(log)
        db.session.commit()

        return redirect(url_for('printer_log'))

    return render_template('log_print.html', materials=materials)

@app.route('/update_status/<int:log_id>/<string:status>')
def update_status(log_id, status):
    log = PrinterLog.query.get_or_404(log_id)
    log.status = status
    log.time_claimed = datetime.now()
    db.session.commit()
    return redirect(url_for('printer_log'))

if __name__ == '__main__':
    app.run(debug=True)
