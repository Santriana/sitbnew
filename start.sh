python manage.py migrate &&
python manage.py collectstatic --noinput &&
python manage.py loaddata fixtures/District.json fixtures/Province.json
echo "from django.contrib.auth import get_user_model;
User = get_user_model();
if User.objects.count() == 0:
    User.objects.create_superuser('admin@admin.com', 'p1np1np1n', )" | python manage.py shell &&
celery -A usaid worker -l info -P solo -f files/logs/celery-worker.log &
celery -A usaid beat -l info -f files/logs/celery-beat.log &
gunicorn usaid.wsgi:application --bind 0.0.0.0:8000

