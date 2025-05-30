from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import LogPrintForm, AddFilamentForm, AddResinForm
from .models import PrintLog, FilamentInventory, ResinInventory
from .utils import generate_unique_code, generate_resin_code
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def dashboard():
    form = LogPrintForm()
    # ... any other code you have here
    return render_template('dashboard.html', log_print_form=form)

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



@views.route('/log_print', methods=['GET', 'POST'])
def log_print():
    return render_template("log_print.html")

@views.route('/activities', methods=['GET', 'POST'])
def activities():
    form = LogPrintForm()
    logs = PrintLog.query.order_by(PrintLog.date_started.desc()).all()  # fetch all logs
    return render_template('activities.html', log_print_form=form, print_logs=logs)

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