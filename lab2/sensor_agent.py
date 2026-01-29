import asyncio
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from datetime import datetime
from disaster_environment import DisasterEnvironment

class SensorAgent(Agent):
    """Agent that monitors and detects disaster events"""
    
    class PerceptionBehaviour(PeriodicBehaviour):
        """Periodic behaviour to sense the environment"""
        
        async def on_start(self):
            print(f"\n{'='*60}")
            print(f"SensorAgent starting perception at {datetime.now()}")
            print(f"{'='*60}\n")
            self.environment = DisasterEnvironment()
            self.event_count = 0
            
        async def run(self):
            """Perceive environment and detect events"""
            self.event_count += 1
            
            print(f"\n--- Perception Cycle {self.event_count} ---")
            
            # Get environmental conditions
            conditions = self.environment.get_environmental_conditions()
            print(f"\n[ENVIRONMENTAL CONDITIONS]")
            print(f"Timestamp: {conditions['timestamp']}")
            print(f"Temperature: {conditions['temperature']}°C")
            print(f"Wind Speed: {conditions['wind_speed']} km/h")
            print(f"Visibility: {conditions['visibility']}")
            print(f"Accessibility: {conditions['accessibility']}")
            
            # Detect disaster events (30% probability)
            import random
            if random.random() < 0.3:
                event = self.environment.generate_disaster_event()
                self.log_disaster_event(event)
            else:
                print("\n[STATUS] No disaster detected - All clear")
            
            print(f"\n{'-'*60}\n")
            
        def log_disaster_event(self, event):
            """Log detected disaster event"""
            print(f"\n🚨 [DISASTER DETECTED] 🚨")
            print(f"Timestamp: {event['timestamp']}")
            print(f"Type: {event['type']}")
            print(f"Location: {event['location']}")
            print(f"Severity: {event['severity']}")
            print(f"Estimated Casualties: {event['casualties']}")
            print(f"Resources Needed: {event['resources_needed']}")
            
            # Write to log file
            with open('disaster_events.log', 'a') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"DISASTER EVENT LOG\n")
                f.write(f"{'='*60}\n")
                f.write(f"Timestamp: {event['timestamp']}\n")
                f.write(f"Type: {event['type']}\n")
                f.write(f"Location: {event['location']}\n")
                f.write(f"Severity: {event['severity']}\n")
                f.write(f"Casualties: {event['casualties']}\n")
                f.write(f"Resources Needed: {event['resources_needed']}\n")
                f.write(f"{'='*60}\n\n")
                
        async def on_end(self):
            print(f"\n{'='*60}")
            print(f"SensorAgent stopping. Total events detected: {self.event_count}")
            print(f"{'='*60}\n")
    
    async def setup(self):
        print(f"\nSensorAgent {self.jid} initializing...")
        # Run perception every 5 seconds
        perception = self.PerceptionBehaviour(period=5)
        self.add_behaviour(perception)

async def main():
    # Replace with your XMPP credentials
    agent_jid = "basicagent1@xmpp.jp"
    agent_password = "password123"
    
    sensor = SensorAgent(agent_jid, agent_password)
    await sensor.start()
    
    print("\nSensorAgent is monitoring the environment...")
    print("Press Ctrl+C to stop\n")
    
    # Run for 30 seconds (6 perception cycles)
    try:
        await asyncio.sleep(30)
    except KeyboardInterrupt:
        print("\n\nStopping agent...")
    
    await sensor.stop()
    print("SensorAgent stopped.")

if __name__ == "__main__":
    asyncio.run(main())