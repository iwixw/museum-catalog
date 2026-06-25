from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.models import MUSEUM_CATEGORIES


class SearchForm(FlaskForm):
    query = StringField('Поиск', validators=[Optional()])
    city = StringField('Город', validators=[Optional()])
    category = SelectField('Категория', validators=[Optional()],
                           choices=[('', 'Все категории')] + MUSEUM_CATEGORIES)
    submit = SubmitField('Найти')

    class Meta:
        csrf = False


class ApplicationForm(FlaskForm):
    museum_name = StringField('Название музея', validators=[
        DataRequired(message='Это поле обязательно для заполнения.'),
        Length(max=200, message='Название не должно превышать 200 символов.')
    ])
    museum_description = TextAreaField('Описание', validators=[
        Optional(),
        Length(max=5000, message='Описание не должно превышать 5000 символов.')
    ])
    museum_city = StringField('Город', validators=[
        DataRequired(message='Это поле обязательно для заполнения.'),
        Length(max=100, message='Название города не должно превышать 100 символов.')
    ])
    museum_category = SelectField('Категория', validators=[
        DataRequired(message='Выберите категорию.')
    ], choices=MUSEUM_CATEGORIES)
    museum_address = StringField('Адрес', validators=[
        Optional(),
        Length(max=300, message='Адрес не должен превышать 300 символов.')
    ])
    museum_phone = StringField('Телефон', validators=[
        Optional(),
        Length(max=50, message='Номер телефона не должен превышать 50 символов.')
    ])
    museum_website = StringField('Сайт', validators=[
        Optional(),
        Length(max=200, message='URL сайта не должен превышать 200 символов.')
    ])
    museum_image_file = FileField('Фото музея', validators=[
        Optional(),
        FileAllowed(['png', 'jpg', 'jpeg', 'webp', 'gif'],
                    message='Допустимые форматы: PNG, JPG, JPEG, WEBP, GIF.')
    ])
    submit = SubmitField('Подать заявку')
