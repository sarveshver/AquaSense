# dashboard/utils.py

import pandas as pd
from datetime import datetime
from .models import SensorData

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR0KS_bWewRyvL1KkdUshVh81DaT5V06meyVrGcP4NDMdbKxtPraaOB5imc_IrBqkib-tONhrtmgwTM/pub?output=csv"

def fetch_live_data():
    try:
        df = pd.read_csv(GOOGLE_SHEET_URL)
        df.columns = df.columns.str.strip()  # Clean column names

        latest = df.iloc[-1]

        SensorData.objects.create(
            tds=float(latest['TDS (ppm)']),
            turbidity=float(latest['Turbidity (NTU)']),
            water_temp=float(latest['Water Temp (°C)']),
            air_temp=float(latest['Air Temp (°C)']) if pd.notna(latest['Air Temp (°C)']) else 0.0
        )

        return {
            'tds': float(latest['TDS (ppm)']),
            'turbidity': float(latest['Turbidity (NTU)']),
            'water_temp': float(latest['Water Temp (°C)']),
            'air_temp': float(latest['Air Temp (°C)']) if pd.notna(latest['Air Temp (°C)']) else 0.0,
            'timestamp': datetime.now().strftime("%H:%M")
        }

    except Exception as e:
        print("❌ Error fetching data from Google Sheet:")
        print(e)
        return None


def get_historical_data(hours=24):
    """Returns the latest 'hours' entries from the DB for plotting"""
    data = SensorData.objects.all().order_by('-timestamp')[:hours]

    return {
        'timestamps': [d.timestamp.strftime("%H:%M") for d in data],
        'tds': [d.tds for d in data],
        'turbidity': [d.turbidity for d in data],
        'water_temp': [d.water_temp for d in data],
        'air_temp': [d.air_temp for d in data]
    }

def get_data_by_date(date_str):
    """Returns all data from SensorData for the given date."""
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        data = SensorData.objects.filter(timestamp__date=selected_date).order_by('timestamp')
        return {
            'timestamps': [d.timestamp.strftime("%H:%M") for d in data],
            'tds': [d.tds for d in data],
            'turbidity': [d.turbidity for d in data],
            'water_temp': [d.water_temp for d in data],
            'air_temp': [d.air_temp for d in data]
        }
    except Exception as e:
        print(f"❌ Error filtering by date: {e}")
        return {
            'timestamps': [],
            'tds': [],
            'turbidity': [],
            'water_temp': [],
            'air_temp': []
        }