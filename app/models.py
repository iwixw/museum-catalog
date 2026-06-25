from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager, bcrypt


MUSEUM_CATEGORIES = [
    ('art', 'Искусство'),
    ('history', 'История'),
    ('science', 'Наука'),
    ('nature', 'Природа'),
    ('technology', 'Технологии'),
    ('other', 'Другое'),
]

CATEGORY_DICT = dict(MUSEUM_CATEGORIES)

APPLICATION_STATUSES = [
    ('pending', 'На рассмотрении'),
    ('approved', 'Одобрена'),
    ('rejected', 'Отклонена'),
]

STATUS_DICT = dict(APPLICATION_STATUSES)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(16), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


class Museum(db.Model):
    __tablename__ = 'museums'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    address = db.Column(db.String(300), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    image_filename = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    photos = db.relationship('MuseumPhoto', backref='museum', lazy='dynamic',
                             cascade='all, delete-orphan', order_by='MuseumPhoto.is_primary.desc()')

    @property
    def category_label(self):
        return CATEGORY_DICT.get(self.category, self.category)

    @property
    def primary_photo(self):
        return self.photos.filter_by(is_primary=True).first() or self.photos.first()

    @property
    def image_src(self):
        from flask import url_for
        p = self.primary_photo
        if p:
            return url_for('static', filename=f'uploads/{p.filename}')
        if self.image_filename:
            return url_for('static', filename=f'uploads/{self.image_filename}')
        return self.image_url or None

    def __repr__(self):
        return f'<Museum {self.name}>'


class MuseumPhoto(db.Model):
    __tablename__ = 'museum_photos'

    id = db.Column(db.Integer, primary_key=True)
    museum_id = db.Column(db.Integer, db.ForeignKey('museums.id'), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def src(self):
        from flask import url_for
        return url_for('static', filename=f'uploads/{self.filename}')

    def __repr__(self):
        return f'<MuseumPhoto {self.filename}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    museum_name = db.Column(db.String(200), nullable=False)
    museum_description = db.Column(db.Text, nullable=True)
    museum_city = db.Column(db.String(100), nullable=False)
    museum_category = db.Column(db.String(50), nullable=False)
    museum_address = db.Column(db.String(300), nullable=True)
    museum_phone = db.Column(db.String(50), nullable=True)
    museum_website = db.Column(db.String(200), nullable=True)
    museum_image_filename = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    admin_comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def category_label(self):
        return CATEGORY_DICT.get(self.museum_category, self.museum_category)

    @property
    def status_label(self):
        return STATUS_DICT.get(self.status, self.status)

    @property
    def museum_image_src(self):
        if self.museum_image_filename:
            from flask import url_for
            return url_for('static', filename=f'uploads/{self.museum_image_filename}')
        return None

    def __repr__(self):
        return f'<Application {self.museum_name} [{self.status}]>'
