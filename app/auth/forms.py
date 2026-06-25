from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Это поле обязательно для заполнения.'),
        Email(message='Введите корректный email адрес.')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Это поле обязательно для заполнения.')
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Это поле обязательно для заполнения.'),
        Length(min=3, max=64, message='Имя пользователя должно быть от 3 до 64 символов.')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Это поле обязательно для заполнения.'),
        Email(message='Введите корректный email адрес.')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Это поле обязательно для заполнения.'),
        Length(min=6, message='Пароль должен содержать не менее 6 символов.')
    ])
    password2 = PasswordField('Повторите пароль', validators=[
        DataRequired(message='Это поле обязательно для заполнения.'),
        EqualTo('password', message='Пароли должны совпадать.')
    ])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError('Это имя пользователя уже занято. Выберите другое.')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError('Этот email уже зарегистрирован.')
