# dashboard/ml_models.py

import numpy as np
from sklearn.linear_model import LinearRegression
from .models import SensorData

def train_prediction_models():
    # Get last 24 hours data
    data = SensorData.objects.all().order_by('-timestamp')[:24]
    
    if len(data) < 3:
        return None, None  # Not enough data
    
    # Prepare data for TDS prediction
    X_tds = np.array(range(len(data))).reshape(-1, 1)
    y_tds = np.array([d.tds for d in data])
    
    # Prepare data for Turbidity prediction
    X_turb = np.array(range(len(data))).reshape(-1, 1)
    y_turb = np.array([d.turbidity for d in data])
    
    # Train simple linear regression models
    model_tds = LinearRegression().fit(X_tds, y_tds)
    model_turb = LinearRegression().fit(X_turb, y_turb)
    
    return model_tds, model_turb

def predict_next_values(model_tds, model_turb):
    if not model_tds or not model_turb:
        return None, None
    
    # Predict next value (time step = len(data) + 1)
    next_tds = model_tds.predict([[24]])[0]
    next_turb = model_turb.predict([[24]])[0]
    
    return next_tds, next_turb