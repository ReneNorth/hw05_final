from datetime import datetime


def year(request):
    current_year = int(datetime.now().strftime("%Y"))
    return {
        'year': current_year
    }
