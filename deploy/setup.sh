#!/bin/bash
# Запускать от root на Ubuntu 22.04

# 1. Обновление системы и установка зависимостей
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx

# 2. Создание папки проекта
mkdir -p /var/www/museums
cd /var/www/museums

# 3. Виртуальное окружение и зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Инициализация БД
python run.py &
sleep 3
kill %1

# 5. Права на папку загрузок
chown -R www-data:www-data /var/www/museums
chmod -R 755 /var/www/museums

# 6. Systemd сервис
cp deploy/museums.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable museums
systemctl start museums

# 7. Nginx
cp deploy/museums.nginx /etc/nginx/sites-available/museums
ln -s /etc/nginx/sites-available/museums /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "Готово! Сайт доступен по адресу сервера."
