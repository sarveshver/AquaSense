# dashboard/views.py

from django.shortcuts import render
from django.http import JsonResponse
from .utils import fetch_live_data, get_historical_data
from .ml_model import train_prediction_models, predict_next_values
import json
from django.views.decorators.csrf import csrf_exempt

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
        live_data = fetch_live_data()
        historical_data = get_historical_data()
        
        # Train models and get predictions
        model_tds, model_turb = train_prediction_models()
        pred_tds, pred_turb = predict_next_values(model_tds, model_turb)
        
        return JsonResponse({
            'live_data': live_data,
            'historical_data': historical_data,
            'predictions': {
                'tds': pred_tds,
                'turbidity': pred_turb,
                'trend': 'stable'
            }
        })