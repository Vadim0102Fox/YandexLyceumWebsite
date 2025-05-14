from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired


class ConfirmForm(FlaskForm):
    confirm = SubmitField('Подтвердить', validators=[DataRequired()])
