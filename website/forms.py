from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, DateField, TimeField, IntegerField
from wtforms.validators import DataRequired, Optional
from datetime import date, datetime

# Form to add inventory items
class AddItemForm(FlaskForm):
    type = SelectField('Type', choices=[('Filament', 'Filament'), ('Resin', 'Resin')], validators=[DataRequired()])
    material = SelectField('Material', choices=[], validators=[DataRequired()])
    new_material = StringField('New Material', validators=[Optional()])
    color = SelectField('Color', choices=[], validators=[DataRequired()])
    new_color = StringField('New Color', validators=[Optional()])
    size = SelectField('Size', choices=[('1.75mm', '1.75mm'), ('2.85mm', '2.85mm')], validators=[Optional()])
    approx_weight = FloatField('Approx Weight (g)', validators=[DataRequired()])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired()])

# Form to log 3D prints
class LogPrintForm(FlaskForm):
    date_started = DateField('Date Started', format='%Y-%m-%d', default=date.today, validators=[DataRequired()])
    time_started = TimeField('Time Started', format='%H:%M', default=datetime.now().time, validators=[DataRequired()])
    model_name = StringField('Model Name', validators=[DataRequired()])
    printer_id = SelectField('Printer', choices=[], validators=[DataRequired()])
    material_id = SelectField('Material', choices=[], validators=[DataRequired()])
    material_used = FloatField('Amount Used (g)', validators=[DataRequired()])
    print_duration = StringField('Print Duration (in minutes)', validators=[DataRequired()])
    layer_height = FloatField('Layer Height (mm)', validators=[Optional()])
    nozzle_temp = FloatField('Nozzle Temp (°C)', validators=[Optional()])
    bed_temp = FloatField('Bed Temp (°C)', validators=[Optional()])
    chamber_temp = FloatField('Chamber Temp (°C)', validators=[Optional()])
    submit = SubmitField('Log Print')
