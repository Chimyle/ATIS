from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, DateField, TimeField, IntegerField
from wtforms.validators import DataRequired, Optional
from datetime import date, datetime

# Form to add inventory items
class AddFilamentForm(FlaskForm):
    material = SelectField('Material', coerce=str, validators=[DataRequired()])
    new_material = StringField('New Material', validators=[Optional()])
    color = SelectField('Color', coerce=str, validators=[DataRequired()])
    new_color = StringField('New Color', validators=[Optional()])
    size = SelectField('Size', choices=[('1.75mm', '1.75mm'), ('2.85mm', '2.85mm')])
    approx_weight = FloatField('Approx Weight (g)', validators=[DataRequired()])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired()])


class AddResinForm(FlaskForm):
    material = SelectField('Material', coerce=str, validators=[DataRequired()])
    new_material = StringField('New Material', validators=[Optional()])
    printer = SelectField('Printer', choices=[
        ('Formlabs', 'Formlabs'),       
        ('Phrozen', 'Phrozen')], validators=[DataRequired()])
    date_mfg = DateField('Date of Manufacture', validators=[Optional()])
    date_expiry = DateField('Date of Expiry', validators=[Optional()])
    date_delivered = DateField('Date Delivered', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Sealed', 'Sealed'),
        ('Opened', 'Opened'),
        ('In Use', 'In Use'),
        ('Expired', 'Expired'),
        ('Damaged', 'Damaged')
    ], validators=[Optional()])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired()])


# Form to log 3D prints
class LogPrintForm(FlaskForm):
    date_started = DateField('Date Started', format='%Y-%m-%d', default=date.today, validators=[DataRequired()])
    time_started = TimeField('Time Started', format='%H:%M', default=datetime.now().time, validators=[DataRequired()])
    model_name = StringField('Model Name', validators=[DataRequired()])
    printer_id = SelectField('Printer', choices=[
        ('Bambulab P1P', 'Bambulab P1P'),
        ('Bambulab X1C', 'Bambulab X1C'),
        ('Ender 3', 'Ender 3'),
        ('Ender 3 Max', 'Ender 3 Max'),
        ('Intamsys Low', 'Intamsys Low'),
        ('Intamsys High', 'Intamsys High'),
        ('Modix', 'Modix'),
        ('Prusa Orange', 'Prusa Orange'),
        ('Prusa Black', 'Prusa Black'),       
        ('Ultimaker', 'Ultimaker')], validators=[DataRequired()])
    material_code = SelectField('Material ID', coerce=str, validators=[DataRequired()])
    material_used = FloatField('Amount Used (g)', validators=[DataRequired()])
    print_duration = StringField('Print Duration (in minutes)', validators=[DataRequired()])
    layer_height = FloatField('Layer Height (mm)', validators=[Optional()])
    nozzle_temp = FloatField('Nozzle Temp (°C)', validators=[Optional()])
    bed_temp = FloatField('Bed Temp (°C)', validators=[Optional()])
    chamber_temp = FloatField('Chamber Temp (°C)', validators=[Optional()])
    submit = SubmitField('Log Print')
