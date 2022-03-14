from django.utils import timezone as tz


def year(request):
    """Добавляет переменную с текущим годом."""
    year = tz.now().year
    return {'year': year}
