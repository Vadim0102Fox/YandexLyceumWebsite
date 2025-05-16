from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, EmailField, IntegerField, PasswordField
from flask_wtf.file import FileAllowed

class EditUserForm(FlaskForm):
    name = StringField('Имя пользователя')
    description = StringField('Описание профиля')
    avatar = FileField('Изображение профиля', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!')])
    email = EmailField('Почта')
    password = PasswordField('Пароль')
    role = IntegerField('Роль (1 - пользователь, 2 - администратор)')
    submit = SubmitField('Опубликовать')
