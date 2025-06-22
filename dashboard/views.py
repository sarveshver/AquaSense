# dashboard/views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .utils import fetch_live_data, get_historical_data, get_data_by_date
from .ml_model import train_prediction_models, predict_next_values
from .models import SensorData
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import TruncDate
import pandas as pd
from datetime import datetime


def dashboard(request):
    # Get latest data
    live_data = fetch_live_data()
    historical_data = get_historical_data()

    # Train models and get predictions
    model_tds, model_turb = train_prediction_models()
    pred_tds, pred_turb = predict_next_values(model_tds, model_turb)

    context = {
        'live_data': live_data,
        'historical_data': historical_data,
        'predictions': {
            'tds': pred_tds,
            'turbidity': pred_turb,
            'trend': 'stable'  # You can implement trend detection
        }
    }

    return render(request, 'dashboard/index.html', context)


@csrf_exempt
def update_data(request):
    if request.method == 'GET':
        date = request.GET.get('date')

        if date:
            # Only show historical data for selected date
            historical_data = get_data_by_date(date)
            live_data = {}  # No live data for past
            predictions = {
                'tds': None,
                'turbidity': None,
                'trend': 'historical'
            }
        else:
            # Show live data and 24h history
            live_data = fetch_live_data()
            historical_data = get_historical_data()
            model_tds, model_turb = train_prediction_models()
            pred_tds, pred_turb = predict_next_values(model_tds, model_turb)
            predictions = {
                'tds': pred_tds,
                'turbidity': pred_turb,
                'trend': 'stable'
            }

        return JsonResponse({
            'live_data': live_data,
            'historical_data': historical_data,
            'predictions': predictions
        })


def available_dates(request):
    dates = SensorData.objects.annotate(day=TruncDate('timestamp')) \
                              .values_list('day', flat=True) \
                              .distinct().order_by('-day')
    return JsonResponse({'dates': list(dates)})

def download_excel(request):
    date = request.GET.get('date')
    if date:
        records = SensorData.objects.filter(timestamp__date=date)
    else:
        records = SensorData.objects.all().order_by('-timestamp')[:100]

    if not records.exists():
        return HttpResponse("No data available for export.", status=404)

    df = pd.DataFrame.from_records(records.values(
        'timestamp', 'tds', 'turbidity', 'water_temp', 'air_temp'
    ))

    df.rename(columns={
        'timestamp': 'Timestamp',
        'tds': 'TDS (ppm)',
        'turbidity': 'Turbidity (NTU)',
        'water_temp': 'Water Temp (°C)',
        'air_temp': 'Air Temp (°C)'
    }, inplace=True)

    # ✅ Fix timezone issue
    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"aquasense_data_{date or 'latest'}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    df.to_excel(response, index=False, engine='openpyxl')
    return response
