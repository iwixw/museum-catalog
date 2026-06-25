from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.main import main
from app.main.forms import SearchForm, ApplicationForm
from app.models import Museum, Application, MUSEUM_CATEGORIES
from app.utils import save_image


@main.route('/')
def index():
    recent_museums = Museum.query.order_by(Museum.created_at.desc()).limit(6).all()
    total_museums = Museum.query.count()
    cities = db.session.query(Museum.city).distinct().count()
    return render_template('index.html',
                           title='Каталог музеев',
                           recent_museums=recent_museums,
                           total_museums=total_museums,
                           cities=cities)


@main.route('/museums')
def museums():
    form = SearchForm(request.args)
    query = Museum.query

    search_query = request.args.get('query', '').strip()
    city_filter = request.args.get('city', '').strip()
    category_filter = request.args.get('category', '').strip()

    if search_query:
        query = query.filter(Museum.name.ilike(f'%{search_query}%'))
    if city_filter:
        query = query.filter(Museum.city.ilike(f'%{city_filter}%'))
    if category_filter:
        query = query.filter(Museum.category == category_filter)

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Museum.name).paginate(page=page, per_page=12, error_out=False)
    museums_list = pagination.items

    all_cities = db.session.query(Museum.city).distinct().order_by(Museum.city).all()
    all_cities = [c[0] for c in all_cities]

    return render_template('main/museums.html',
                           title='Музеи',
                           form=form,
                           museums=museums_list,
                           pagination=pagination,
                           categories=MUSEUM_CATEGORIES,
                           all_cities=all_cities,
                           search_query=search_query,
                           city_filter=city_filter,
                           category_filter=category_filter)


@main.route('/museums/<int:museum_id>')
def museum_detail(museum_id):
    museum = Museum.query.get_or_404(museum_id)
    return render_template('main/museum_detail.html',
                           title=museum.name,
                           museum=museum)


@main.route('/submit-application', methods=['GET', 'POST'])
@login_required
def submit_application():
    form = ApplicationForm()
    if form.validate_on_submit():
        image_filename = save_image(form.museum_image_file.data)
        application = Application(
            user_id=current_user.id,
            museum_name=form.museum_name.data,
            museum_description=form.museum_description.data,
            museum_city=form.museum_city.data,
            museum_category=form.museum_category.data,
            museum_address=form.museum_address.data,
            museum_phone=form.museum_phone.data,
            museum_website=form.museum_website.data,
            museum_image_filename=image_filename,
            status='pending'
        )
        db.session.add(application)
        db.session.commit()
        flash('Ваша заявка успешно подана и находится на рассмотрении.', 'success')
        return redirect(url_for('main.my_applications'))
    return render_template('main/submit_application.html',
                           title='Подать заявку',
                           form=form)


@main.route('/my-applications')
@login_required
def my_applications():
    applications = Application.query.filter_by(user_id=current_user.id)\
        .order_by(Application.created_at.desc()).all()
    return render_template('main/my_applications.html',
                           title='Мои заявки',
                           applications=applications)
