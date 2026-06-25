from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.models import MUSEUM_CATEGORIES


class MuseumForm(FlaskForm):
    name = StringField('Название музея', validators=[
        DataRequired(message='Это поле обязательно для заполнения.'),
        Length(max=200, message='Название не должно превышать 200 символов.')
    ])
    description = TextAreaField('Описание', validators=[
        Optional(),
        Length(max=5000, message='Описание не должно превышать 5000 символов.')
    ])
    city = StringField('Город', validators=[
        DataRequired(message='Это поле обязательно для заполнения.'),
        Length(max=100, message='Название города не должно превышать 100 символов.')
    ])
    category = SelectField('Категория', validators=[
        DataRequired(message='Выберите категорию.')
    ], choices=MUSEUM_CATEGORIES)
    address = StringField('Адрес', validators=[
        Optional(),
        Length(max=300, message='Адрес не должен превышать 300 символов.')
    ])
    phone = StringField('Телефон', validators=[
        Optional(),
        Length(max=50, message='Номер телефона не должен превышать 50 символов.')
    ])
    website = StringField('Сайт', validators=[
        Optional(),
        Length(max=200, message='URL сайта не должен превышать 200 символов.')
    ])
    image_file = FileField('Загрузить фото', validators=[
        Optional(),
        FileAllowed(['png', 'jpg', 'jpeg', 'webp', 'gif'],
                    message='Допустимые форматы: PNG, JPG, JPEG, WEBP, GIF.')
    ])
    image_url = StringField('или URL изображения', validators=[
        Optional(),
        Length(max=500, message='URL изображения не должен превышать 500 символов.')
    ])
    submit = SubmitField('Сохранить')


class ApplicationReviewForm(FlaskForm):
    admin_comment = TextAreaField('Комментарий администратора', validators=[
        Optional(),
        Length(max=1000, message='Комментарий не должен превышать 1000 символов.')
    ])
    approve = SubmitField('Одобрить')
    reject = SubmitField('Отклонить')
