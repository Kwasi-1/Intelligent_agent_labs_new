import random
import time
from datetime import datetime

class DisasterEnvironment:
    """Simulates a disaster environment with various events"""
    
    def __init__(self):
        self.disaster_types = ['Fire', 'Flood', 'Earthquake', 'Storm']
        self.severity_levels = ['Low', 'Medium', 'High', 'Critical']
        self.locations = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']
        
    def generate_disaster_event(self):
        """Generate a random disaster event"""
        event = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': random.choice(self.disaster_types),
            'location': random.choice(self.locations),
            'severity': random.choice(self.severity_levels),
            'casualties': random.randint(0, 50),
            'resources_needed': random.choice(['Medical', 'Food', 'Shelter', 'Rescue'])
        }
        return event
    
    def get_environmental_conditions(self):
        """Get current environmental conditions"""
        conditions = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'temperature': random.randint(15, 40),
            'wind_speed': random.randint(0, 100),
            'visibility': random.choice(['Clear', 'Moderate', 'Poor']),
            'accessibility': random.choice(['Normal', 'Restricted', 'Blocked'])
        }
        return conditions