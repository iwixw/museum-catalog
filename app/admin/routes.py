from datetime import datetime
from functools import wraps
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.admin import admin
from app.admin.forms import MuseumForm, ApplicationReviewForm
from app.models import Museum, MuseumPhoto, Application, User, MUSEUM_CATEGORIES
from app.utils import save_image, delete_image


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/')
@login_required
@admin_required
def dashboard():
    total_museums = Museum.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_applications = Application.query.count()
    pending_applications = Application.query.filter_by(status='pending').count()
    approved_applications = Application.query.filter_by(status='approved').count()
    rejected_applications = Application.query.filter_by(status='rejected').count()
    recent_applications = Application.query.order_by(Application.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           title='Панель администратора',
                           total_museums=total_museums,
                           total_users=total_users,
                           total_applications=total_applications,
                           pending_applications=pending_applications,
                           approved_applications=approved_applications,
                           rejected_applications=rejected_applications,
                           recent_applications=recent_applications)


@admin.route('/museums')
@login_required
@admin_required
def museums():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    query = Museum.query
    if search:
        query = query.filter(Museum.name.ilike(f'%{search}%'))
    pagination = query.order_by(Museum.name).paginate(page=page, per_page=15, error_out=False)
    return render_template('admin/museums.html',
                           title='Управление музеями',
                           museums=pagination.items,
                           pagination=pagination,
                           search=search)


@admin.route('/museums/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_museum():
    form = MuseumForm()
    if form.validate_on_submit():
        museum = Museum(
            name=form.name.data,
            description=form.description.data,
            city=form.city.data,
            category=form.category.data,
            address=form.address.data,
            phone=form.phone.data,
            website=form.website.data,
            image_url=form.image_url.data or None
        )
        db.session.add(museum)
        db.session.flush()
        _save_gallery_photos(museum, first_is_primary=True)
        db.session.commit()
        flash(f'Музей "{museum.name}" успешно добавлен.', 'success')
        return redirect(url_for('admin.museums'))
    return render_template('admin/museum_form.html',
                           title='Добавить музей',
                           form=form,
                           action='add')


@admin.route('/museums/<int:museum_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_museum(museum_id):
    museum = Museum.query.get_or_404(museum_id)
    form = MuseumForm(obj=museum)
    if form.validate_on_submit():
        museum.name = form.name.data
        museum.description = form.description.data
        museum.city = form.city.data
        museum.category = form.category.data
        museum.address = form.address.data
        museum.phone = form.phone.data
        museum.website = form.website.data
        museum.image_url = form.image_url.data or None
        has_photos = museum.photos.count() > 0
        _save_gallery_photos(museum, first_is_primary=not has_photos)
        db.session.commit()
        flash(f'Музей "{museum.name}" успешно обновлён.', 'success')
        return redirect(url_for('admin.edit_museum', museum_id=museum_id))
    return render_template('admin/museum_form.html',
                           title='Редактировать музей',
                           form=form,
                           museum=museum,
                           action='edit')


def _save_gallery_photos(museum, first_is_primary=False):
    """Сохраняет загруженные файлы из request.files в галерею музея."""
    from flask import request as req
    files = req.files.getlist('gallery_files')
    is_first = True
    for f in files:
        if not f or not f.filename:
            continue
        filename = save_image(f)
        if filename:
            make_primary = first_is_primary and is_first
            photo = MuseumPhoto(museum_id=museum.id, filename=filename, is_primary=make_primary)
            db.session.add(photo)
            is_first = False


@admin.route('/museums/<int:museum_id>/photos/<int:photo_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_museum_photo(museum_id, photo_id):
    photo = MuseumPhoto.query.filter_by(id=photo_id, museum_id=museum_id).first_or_404()
    was_primary = photo.is_primary
    delete_image(photo.filename)
    db.session.delete(photo)
    db.session.flush()
    if was_primary:
        next_photo = MuseumPhoto.query.filter_by(museum_id=museum_id).first()
        if next_photo:
            next_photo.is_primary = True
    db.session.commit()
    flash('Фото удалено.', 'success')
    return redirect(url_for('admin.edit_museum', museum_id=museum_id))


@admin.route('/museums/<int:museum_id>/photos/<int:photo_id>/set-primary', methods=['POST'])
@login_required
@admin_required
def set_primary_photo(museum_id, photo_id):
    all_photos = MuseumPhoto.query.filter_by(museum_id=museum_id).all()
    for p in all_photos:
        p.is_primary = False
    photo = MuseumPhoto.query.filter_by(id=photo_id, museum_id=museum_id).first_or_404()
    photo.is_primary = True
    db.session.commit()
    flash('Главное фото обновлено.', 'success')
    return redirect(url_for('admin.edit_museum', museum_id=museum_id))


@admin.route('/museums/<int:museum_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_museum(museum_id):
    museum = Museum.query.get_or_404(museum_id)
    name = museum.name
    delete_image(museum.image_filename)
    db.session.delete(museum)
    db.session.commit()
    flash(f'Музей "{name}" успешно удалён.', 'success')
    return redirect(url_for('admin.museums'))


@admin.route('/applications')
@login_required
@admin_required
def applications():
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    query = Application.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    pagination = query.order_by(Application.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False)
    return render_template('admin/applications.html',
                           title='Заявки',
                           applications=pagination.items,
                           pagination=pagination,
                           status_filter=status_filter)


@admin.route('/applications/<int:application_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def application_detail(application_id):
    application = Application.query.get_or_404(application_id)
    form = ApplicationReviewForm()
    if form.validate_on_submit():
        application.admin_comment = form.admin_comment.data
        application.updated_at = datetime.utcnow()
        if form.approve.data:
            application.status = 'approved'
            museum = Museum(
                name=application.museum_name,
                description=application.museum_description,
                city=application.museum_city,
                category=application.museum_category,
                address=application.museum_address,
                phone=application.museum_phone,
                website=application.museum_website,
                image_filename=application.museum_image_filename
            )
            db.session.add(museum)
            db.session.commit()
            flash(f'Заявка одобрена. Музей "{application.museum_name}" добавлен в каталог.', 'success')
        elif form.reject.data:
            application.status = 'rejected'
            db.session.commit()
            flash('Заявка отклонена.', 'warning')
        return redirect(url_for('admin.applications'))
    if application.admin_comment:
        form.admin_comment.data = application.admin_comment
    return render_template('admin/application_detail.html',
                           title='Заявка на добавление музея',
                           application=application,
                           form=form)
