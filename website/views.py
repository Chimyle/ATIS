from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import AddItemForm, LogPrintForm
from .models import InventoryItem, PrintLog
from .utils import generate_unique_code
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def dashboard():
    form = LogPrintForm()
    # ... any other code you have here
    return render_template('dashboard.html', log_print_form=form)

# @views.route('/add_item', methods=['POST'])
# def add_item():
#     form = AddItemForm()

#     if form.validate_on_submit():
#         material = request.form.get("material")
#         new_material = request.form.get("new_material")

#         color = request.form.get("color")
#         new_color = request.form.get("new_color")

#         size = request.form.get("size")
#         weight = request.form.get("approx_weight")
#         quantity = int(request.form.get("quantity", 1))

#         # Determine actual values
#         material = new_material.strip() if material == "__new__" and new_material.strip() else material
#         color = new_color.strip() if color == "__new__" and new_color.strip() else color

#         for _ in range(quantity):
#             code = generate_unique_code(material, color, size)

#             item = InventoryItem(
#                 code=code,
#                 type=form.type.data,
#                 material=material,
#                 color=color,
#                 size=size,
#                 weight_remaining=weight
#             )

#             db.session.add(item)

#         db.session.commit()
#         flash(f"{quantity} item(s) added.", "success")

#     return redirect(url_for("views.inventory"))




@views.route('/inventory', methods=['GET', 'POST'])
def inventory():
    form = AddItemForm()
    materials = db.session.query(InventoryItem.material).distinct().all()
    colors = db.session.query(InventoryItem.color).distinct().all()
    # Flatten the list of tuples
    materials = [m[0] for m in materials]
    colors = [c[0] for c in colors]
    form.material.choices = [(m, m) for m in materials] + [("__new__", "Add New")]
    form.color.choices = [(c, c) for c in colors] + [("__new__", "Add New")]
    

    if request.method == 'POST':
        if form.validate_on_submit():
            # Decide material and color values
            material = form.new_material.data if form.material.data == '__new__' else form.material.data
            color = form.new_color.data if form.color.data == '__new__' else form.color.data
            
            # Add new material/color to DB if needed
            # if form.material.data == '__new__':
            #     add_material_to_db(material)
            # if form.color.data == '__new__':
            #     add_color_to_db(color)
            
            # Prepare other data from form
            size = form.size.data
            type_ = form.type.data
            weight = form.approx_weight.data
            quantity = form.quantity.data

            # Generate code, create inventory items, etc
            # Add to db.session and commit
            new_item = InventoryItem(
                code=generate_unique_code(material, color, size),
                type=type_,
                material=material,
                color=color,
                size=size,
                weight_remaining=weight,
                # ... other fields
            )
            db.session.add(new_item)
            db.session.commit()

            flash('Item(s) added!', 'success')
            return redirect(url_for('views.inventory'))

    # If GET or form invalid, just render page with form
    inventory = InventoryItem.query.all()
    return render_template('inventory.html', inventory=inventory, add_item_form=form)


@views.route('/log_print', methods=['GET', 'POST'])
def log_print():
    return render_template("log_print.html")

@views.route('/activities', methods=['GET', 'POST'])
def activities():
    form = LogPrintForm()
    logs = PrintLog.query.order_by(PrintLog.date_started.desc()).all()  # fetch all logs
    return render_template('activities.html', log_print_form=form, print_logs=logs)

@views.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete item.', 'danger')
    return redirect(url_for('views.inventory'))