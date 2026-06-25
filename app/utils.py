import os
import uuid
from flask import current_app


def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_image(file):
    """Сохраняет загруженный файл и возвращает имя файла, или None при ошибке."""
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)
    return filename


def delete_image(filename):
    """Удаляет файл из папки uploads, если он существует."""
    if not filename:
        return
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
