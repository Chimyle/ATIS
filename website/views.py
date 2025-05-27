from flask import Blueprint, render_template, request, redirect, url_for, flash

views = Blueprint('views', __name__)


@views.route('/')
def dashboard():
    return render_template("dashboard.html")

@views.route('/add_item')
def add_item():
    return render_template("add_item.html")

@views.route('/inventory')
def inventory():
    return render_template("inventory.html")

@views.route('/log_print')
def log_print():
    return render_template("log_print.html")

@views.route('/activities')
def activities():
    return render_template("activities.html")