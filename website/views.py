from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import date, datetime
import pandas as pd
from io import BytesIO
from flask import send_file
from .forms import LogPrintForm, AddFilamentForm, AddResinForm
from .models import PrintLog, FilamentInventory, ResinInventory
from .utils import generate_unique_code, generate_resin_code
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def dashboard():
    form = LogPrintForm()
    #logs = PrintLog.query.order_by(PrintLog.date_started.desc()).all()  # fetch all logs
    fmatid = db.session.query(FilamentInventory.id, FilamentInventory.code).all()
    form.material_code.choices = [(str(item.id), item.code) for item in fmatid]

    if form.validate_on_submit():
        new_log = PrintLog(
            date_started=form.date_started.data,
            time_started=form.time_started.data,
            model_name=form.model_name.data,
            printer_name=form.printer_id.data,
            material_code=form.material_code.data,
            material_used=form.material_used.data,
            duration=int(form.print_duration.data),
            layer_height=form.layer_height.data,
            nozzle_temp=form.nozzle_temp.data,
            bed_temp=form.bed_temp.data,
            chamber_temp=form.chamber_temp.data
        )
        db.session.add(new_log)
        db.session.commit()
        flash('Print log added successfully!', 'success')
        return redirect(url_for('views.dashboard'))
    active_jobs = PrintLog.query.filter_by(status='Active').order_by(PrintLog.date_started.desc()).all()
    return render_template('dashboard.html', log_print_form=form, active_jobs=active_jobs)



@views.route('/inventory', methods=['GET', 'POST'])
def inventory():
    filament_form = AddFilamentForm()
    resin_form = AddResinForm()

    # Material & color choices for filament
    fmat = db.session.query(FilamentInventory.material).distinct().all()
    fcol = db.session.query(FilamentInventory.color).distinct().all()
    fmat = [m[0] for m in fmat]
    fcol = [c[0] for c in fcol]

    rmat = db.session.query(ResinInventory.material).distinct().all()
    rmat = [m[0] for m in rmat]

    filament_form.material.choices = [(m, m) for m in fmat] + [("__new__", "Add New")]
    filament_form.color.choices = [(c, c) for c in fcol] + [("__new__", "Add New")]
    resin_form.material.choices = [(m, m) for m in rmat] + [("__new__", "Add New")]

    if filament_form.validate_on_submit():
        material = filament_form.new_material.data if filament_form.material.data == '__new__' else filament_form.material.data
        color = filament_form.new_color.data if filament_form.color.data == '__new__' else filament_form.color.data
        
        for _ in range(filament_form.quantity.data):
            new_item = FilamentInventory(
                code=generate_unique_code(material, color, filament_form.size.data),
                material=material,
                color=color,
                size=filament_form.size.data,
                weight_remaining=filament_form.approx_weight.data
            )
            db.session.add(new_item)
        db.session.commit()
        flash("Filament added!", "success")
        return redirect(url_for('views.inventory'))

    elif resin_form.validate_on_submit():
        material = resin_form.new_material.data if resin_form.material.data == '__new__' else resin_form.material.data
        for _ in range(resin_form.quantity.data):
            new_item = ResinInventory(
                material=material,
                material_code=generate_resin_code(material),
                printer=resin_form.printer.data,
                date_mfg=resin_form.date_mfg.data,
                date_expiry=resin_form.date_expiry.data,
                date_delivered=resin_form.date_delivered.data,
                date_opened=None,  # Resin items don't have an opened date initially
                status=resin_form.status.data if resin_form.status.data else 'Sealed',
            )
            db.session.add(new_item)
        db.session.commit()
        flash("Resin added!", "success")
        return redirect(url_for('views.inventory'))

    finv = FilamentInventory.query.all()
    rinv = ResinInventory.query.all()
    return render_template("inventory.html", finv=finv, rinv=rinv, filament_form=filament_form, resin_form=resin_form)

@views.route('/activities', methods=['GET', 'POST'])
def activities():
    form = LogPrintForm()
    logs = PrintLog.query.order_by(PrintLog.date_started.desc()).all()  # fetch all logs
    fmatid = db.session.query(FilamentInventory.id, FilamentInventory.code).all()
    form.material_code.choices = [(str(item.id), item.code) for item in fmatid]

    if form.validate_on_submit():
        new_log = PrintLog(
            date_started=form.date_started.data,
            time_started=form.time_started.data,
            model_name=form.model_name.data,
            printer_name=form.printer_id.data,
            material_code=form.material_code.data,
            material_used=form.material_used.data,
            duration=int(form.print_duration.data),
            layer_height=form.layer_height.data,
            nozzle_temp=form.nozzle_temp.data,
            bed_temp=form.bed_temp.data,
            chamber_temp=form.chamber_temp.data
        )
        db.session.add(new_log)
        db.session.commit()
        flash('Print log added successfully!', 'success')
        return redirect(url_for('views.activities'))
    logs = PrintLog.query.order_by(PrintLog.date_started.desc()).all()
    return render_template('activities.html', log_print_form=form, logs=logs)

@views.route('/delete_filament/<int:item_id>', methods=['POST'])
def delete_filament(item_id):
    item = FilamentInventory.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete item.', 'danger')
    return redirect(url_for('views.inventory'))
@views.route('/delete_resin/<int:item_id>', methods=['POST'])
def delete_resin(item_id):
    item = ResinInventory.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete item.', 'danger')
    return redirect(url_for('views.inventory'))

@views.route('/delete_log/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    log = PrintLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    flash(f'Log for "{log.model_name}" has been deleted.', 'success')
    return redirect(url_for('views.activities'))

@views.route('/update_status/<int:job_id>', methods=['POST'])
def update_status(job_id):
    job = PrintLog.query.get_or_404(job_id)
    new_status = request.form.get('status')

    if new_status == 'Done':
        job.status = new_status
        job.time_claimed = datetime.now().time().replace(microsecond=0)

        # Subtract material used from corresponding filament inventory
        filament = FilamentInventory.query.get(int(job.material_code))
        if filament:
            filament.weight_remaining = max(filament.weight_remaining - job.material_used, 0)

        db.session.commit()
        flash(f'{job.model_name} marked as Done and material usage recorded.', 'success')

    elif new_status == 'Fail':
        job.status = new_status
        db.session.commit()
        flash(f'{job.model_name} marked as Fail.', 'warning')

    else:
        flash('Invalid status update.', 'danger')

    return redirect(url_for('views.dashboard'))

@views.route('/export/inventory')
def export_inventory():
    # Query data
    filaments = FilamentInventory.query.all()
    resins = ResinInventory.query.all()

    # Convert to list of dicts for pandas
    filament_data = [{
        'Code': f.code,
        'Material': f.material,
        'Color': f.color,
        'Size': f.size,
        'Weight Remaining (g)': f.weight_remaining,
        'Location': f.location
    } for f in filaments]

    resin_data = [{
        'Code': r.material_code,
        'Material': r.material,
        'Printer': r.printer,
        'Manufactured': r.date_mfg,
        'Expiry': r.date_expiry,
        'Status': r.status
    } for r in resins]

    # Create dataframes
    df_filament = pd.DataFrame(filament_data)
    df_resin = pd.DataFrame(resin_data)

    # Create Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_filament.to_excel(writer, index=False, sheet_name='Filament')
        df_resin.to_excel(writer, index=False, sheet_name='Resin')
    output.seek(0)

    # Send file to client
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='inventory_export.xlsx'
    )
@views.route('/export/print_logs')
def export_print_logs():
    # Query all print logs
    logs = PrintLog.query.all()

    # Build list of dicts
    log_data = [{
        'Date Started': log.date_started,
        'Time Started': log.time_started,
        'Model Name': log.model_name,
        'Printer': log.printer_name,
        'Material Code': log.material_code,
        'Material Used (g)': log.material_used,
        'Duration (min)': log.duration,
        'Layer Height': log.layer_height,
        'Nozzle Temp (°C)': log.nozzle_temp,
        'Bed Temp (°C)': log.bed_temp,
        'Chamber Temp (°C)': log.chamber_temp,
        'Status': log.status,
        'Time Claimed': log.time_claimed
    } for log in logs]

    # Convert to DataFrame
    df_logs = pd.DataFrame(log_data)

    # Write to Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_logs.to_excel(writer, index=False, sheet_name='Print Logs')
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='print_logs_export.xlsx'
    )
