from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class CommentForm(FlaskForm):
    text = StringField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')
