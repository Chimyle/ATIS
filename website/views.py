from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import AddItemForm, LogPrintForm
from .models import InventoryItem, PrintLog
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def dashboard():
    form = LogPrintForm()
    # ... any other code you have here
    return render_template('dashboard.html', log_print_form=form)

@views.route('/add_item')
def add_item():
    return render_template("add_item.html")

from .models import InventoryItem  # Make sure this is imported
from .forms import AddItemForm
from flask import render_template

@views.route('/inventory', methods=['GET', 'POST'])
def inventory():
    # Query distinct materials and colors from DB
    materials = db.session.query(InventoryItem.material).distinct().all()
    colors = db.session.query(InventoryItem.color).distinct().all()

    # Flatten the list of tuples
    materials = [m[0] for m in materials]
    colors = [c[0] for c in colors]

    add_item_form = AddItemForm()

    # Set dropdown choices (with "Add New" option at the end)
    add_item_form.material.choices = [(m, m) for m in materials] + [("__new__", "Add New")]
    add_item_form.color.choices = [(c, c) for c in colors] + [("__new__", "Add New")]

    # Load all inventory items to display
    inventory = InventoryItem.query.all()

    return render_template('inventory.html', add_item_form=add_item_form, inventory=inventory)


@views.route('/log_print')
def log_print():
    return render_template("log_print.html")

@views.route('/activities', methods=['GET', 'POST'])
def activities():
    form = LogPrintForm()
    logs = PrintLog.query.order_by(PrintLog.date_started.desc()).all()  # fetch all logs
    return render_template('activities.html', log_print_form=form, print_logs=logs)
