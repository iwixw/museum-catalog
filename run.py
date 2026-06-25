import os
from datetime import datetime
from app import create_app, db
from app.models import User, Museum

app = create_app()


def _migrate_db():
    """Добавляет новые колонки в существующую БД без потери данных."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), 'museums.db')
    if not os.path.exists(db_path):
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(museums)")
    museum_cols = [row[1] for row in cursor.fetchall()]
    if 'image_filename' not in museum_cols:
        cursor.execute("ALTER TABLE museums ADD COLUMN image_filename VARCHAR(300)")
        print("Added column museums.image_filename")

    cursor.execute("PRAGMA table_info(applications)")
    app_cols = [row[1] for row in cursor.fetchall()]
    if 'museum_image_filename' not in app_cols:
        cursor.execute("ALTER TABLE applications ADD COLUMN museum_image_filename VARCHAR(300)")
        print("Added column applications.museum_image_filename")

    # Таблица галереи фотографий
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS museum_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            museum_id INTEGER NOT NULL REFERENCES museums(id),
            filename VARCHAR(300) NOT NULL,
            is_primary BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def init_db():
    """Create all tables and seed initial data."""
    with app.app_context():
        _migrate_db()
        db.create_all()
        _create_admin()
        _seed_sample_museums()
        print("Database initialised successfully.")


def _create_admin():
    admin = User.query.filter_by(email='admin@museum.ru').first()
    if admin is None:
        admin = User(
            username='admin',
            email='admin@museum.ru',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@museum.ru / admin123")
    else:
        print("Admin user already exists.")


def _seed_sample_museums():
    if Museum.query.count() > 0:
        print("Sample museums already seeded.")
        return

    sample_museums = [
        Museum(
            name='Государственный Эрмитаж',
            description=(
                'Государственный Эрмитаж — один из крупнейших художественных '
                'и культурно-исторических музеев мира. Основан в 1764 году '
                'Екатериной Великой. Коллекция насчитывает более трёх миллионов '
                'предметов искусства и культуры.'
            ),
            city='Санкт-Петербург',
            category='art',
            address='Дворцовая набережная, 34',
            phone='+7 (812) 571-34-65',
            website='https://www.hermitagemuseum.org',
            image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Hermitage_Entrance_2.jpg/1280px-Hermitage_Entrance_2.jpg'
        ),
        Museum(
            name='Государственный Русский музей',
            description=(
                'Государственный Русский музей — крупнейший в мире музей '
                'русского изобразительного искусства. Основан в 1895 году. '
                'Коллекция включает более 400 000 экспонатов.'
            ),
            city='Санкт-Петербург',
            category='art',
            address='Инженерная улица, 4',
            phone='+7 (812) 595-42-48',
            website='https://rusmuseum.ru',
            image_url=''
        ),
        Museum(
            name='Государственный Исторический музей',
            description=(
                'Национальный исторический музей России, расположенный на '
                'Красной площади в Москве. Основан в 1872 году. '
                'Хранит уникальную коллекцию артефактов от эпохи палеолита '
                'до наших дней.'
            ),
            city='Москва',
            category='history',
            address='Красная площадь, 1',
            phone='+7 (495) 692-40-19',
            website='https://shm.ru',
            image_url=''
        ),
        Museum(
            name='Политехнический музей',
            description=(
                'Политехнический музей — один из старейших научно-технических '
                'музеев мира. Основан в 1872 году. Посвящён истории науки '
                'и техники.'
            ),
            city='Москва',
            category='technology',
            address='Новая площадь, 3/4',
            phone='+7 (495) 628-00-14',
            website='https://polytech.one',
            image_url=''
        ),
        Museum(
            name='Государственный Дарвиновский музей',
            description=(
                'Один из крупнейших естественно-научных музеев России. '
                'Коллекция насчитывает около 400 000 единиц хранения. '
                'Основан в 1907 году.'
            ),
            city='Москва',
            category='nature',
            address='улица Вавилова, 57',
            phone='+7 (499) 783-22-53',
            website='https://www.darwin.museum.ru',
            image_url=''
        ),
        Museum(
            name='Музей космонавтики',
            description=(
                'Мемориальный музей космонавтики расположен в основании '
                'монумента «Покорителям космоса» на проспекте Мира. '
                'Рассказывает об истории освоения космоса.'
            ),
            city='Москва',
            category='science',
            address='проспект Мира, 111',
            phone='+7 (495) 683-79-14',
            website='https://www.space-museum.ru',
            image_url=''
        ),
    ]

    for museum in sample_museums:
        db.session.add(museum)
    db.session.commit()
    print(f"Seeded {len(sample_museums)} sample museums.")


@app.context_processor
def inject_globals():
    return {'now': datetime.utcnow()}


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
