# dashboard/models.py

from django.db import models

class SensorData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    tds = models.FloatField()
    turbidity = models.FloatField()
    water_temp = models.FloatField()
    air_temp = models.FloatField()
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Sensor Data at {self.timestamp}"