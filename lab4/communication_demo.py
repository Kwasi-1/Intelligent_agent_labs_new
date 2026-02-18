"""
Lab 4: Agent Communication Using FIPA-ACL
DCIT 403 – Designing Intelligent Agent
Disaster Response & Relief Coordination System

This module implements inter-agent communication using FIPA-ACL performatives.
Uses a single XMPP account with internal message passing to demonstrate:
- SensorAgent behavior sends INFORM messages
- RescueAgent behavior receives and processes messages
- REQUEST performatives for bidirectional communication

FIPA-ACL Performatives Used:
  - INFORM: Notify other agents of disaster events
  - REQUEST: Request information or action from other agents
"""

import asyncio
import json
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message

# Import the disaster environment from Lab 2
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lab2'))
from disaster_environment import DisasterEnvironment


# ═══════════════════════════════════════════════════════════════════
# MESSAGE LOGGING UTILITY
# ═══════════════════════════════════════════════════════════════════

def log_message(direction, sender, receiver, performative, content):
    """Log message details to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    log_entry = f"""
{'='*60}
[{timestamp}] {direction}
{'='*60}
From        : {sender}
To          : {receiver}
Performative: {performative}
Content     : {content}
{'='*60}
"""
    
    print(log_entry)
    
    with open('message_log.txt', 'a') as f:
        f.write(log_entry + '\n')


# ═══════════════════════════════════════════════════════════════════
# UNIFIED AGENT WITH SENSOR AND RESCUE BEHAVIORS
# ═══════════════════════════════════════════════════════════════════

class CommunicationDemoAgent(Agent):
    """
    Single agent demonstrating FIPA-ACL communication using internal message passing.
    This approach works with a single XMPP account.
    """
    
    class SensorBehaviour(PeriodicBehaviour):
        """Simulates SensorAgent - detects disasters and sends INFORM messages"""
        
        async def on_start(self):
            print(f"\n{'*'*60}")
            print(f"[SENSOR BEHAVIOR] Starting detection system...")
            print(f"{'*'*60}\n")
            self.environment = DisasterEnvironment()
            self.detection_count = 0
            
        async def run(self):
            """Detect disasters and send INFORM messages"""
            self.detection_count += 1
            
            print(f"\n--- [SENSOR] Detection Cycle {self.detection_count} ---")
            
            # Get environmental conditions
            conditions = self.environment.get_environmental_conditions()
            print(f"[SENSOR] Monitoring: Temp={conditions['temperature']}°C, "
                  f"Wind={conditions['wind_speed']}km/h, "
                  f"Visibility={conditions['visibility']}")
            
            # 50% chance of detecting a disaster
            import random
            if random.random() < 0.5:
                event = self.environment.generate_disaster_event()
                print(f"\n[SENSOR] 🚨 DISASTER DETECTED: {event['type']} at {event['location']}")
                
                # Send INFORM message
                await self.send_disaster_inform(event)
            else:
                print("[SENSOR] ✓ All clear - no disaster detected")
                
        async def send_disaster_inform(self, event):
            """Send INFORM message about detected disaster"""
            msg = Message(
                to=str(self.agent.jid),  # Send to self (rescue behavior will receive)
                sender=str(self.agent.jid),
                body=json.dumps(event),
                metadata={
                    "performative": "inform",
                    "ontology": "disaster-response",
                    "language": "JSON",
                    "role": "sensor-to-rescue"
                }
            )
            msg.set_metadata("performative", "inform")
            msg.set_metadata("role", "sensor-to-rescue")
            
            await self.send(msg)
            
            log_message(
                direction="OUTGOING INFORM MESSAGE (Sensor → Rescue)",
                sender="SensorBehavior",
                receiver="RescueBehavior",
                performative="INFORM",
                content=f"Disaster: {event['type']} | Location: {event['location']} | "
                        f"Severity: {event['severity']} | Casualties: {event['casualties']} | "
                        f"Resources: {event['resources_needed']}"
            )
    
    
    class RescueBehaviour(CyclicBehaviour):
        """Simulates RescueAgent - receives INFORM messages and triggers actions"""
        
        async def on_start(self):
            print(f"\n{'*'*60}")
            print(f"[RESCUE BEHAVIOR] Starting message receiver...")
            print(f"Listening for disaster alerts...")
            print(f"{'*'*60}\n")
            self.agent.rescue_responses = 0
            
        async def run(self):
            """Receive and process messages"""
            msg = await self.receive(timeout=10)
            
            if msg:
                performative = msg.get_metadata("performative")
                role = msg.get_metadata("role")
                
                # Only process sensor-to-rescue messages
                if role == "sensor-to-rescue":
                    log_message(
                        direction="INCOMING MESSAGE (Sensor → Rescue)",
                        sender="SensorBehavior",
                        receiver="RescueBehavior",
                        performative=performative.upper() if performative else "UNKNOWN",
                        content=msg.body[:200]
                    )
                    
                    # Parse and handle the message
                    if performative == "inform":
                        await self.handle_inform(msg)
                        
                elif role == "rescue-to-sensor" and performative == "request":
                    # Handle REQUEST responses from rescue back to sensor
                    pass
                    
        async def handle_inform(self, msg):
            """Handle INFORM messages about disasters"""
            try:
                event = json.loads(msg.body)
                
                print(f"\n{'─'*60}")
                print(f"[RESCUE] Processing disaster alert...")
                print(f"  Type     : {event['type']}")
                print(f"  Location : {event['location']}")
                print(f"  Severity : {event['severity']}")
                print(f"  Casualties: {event['casualties']}")
                print(f"  Resources: {event['resources_needed']}")
                
                # Trigger action based on severity
                if event['severity'] in ('Medium', 'High', 'Critical'):
                    print(f"\n  🚁 ACTION: Deploying rescue team to {event['location']}")
                    print(f"  📦 Allocating resources: {event['resources_needed']}")
                    self.agent.rescue_responses += 1
                    
                    # Send REQUEST for additional information on Critical events
                    if event['severity'] == 'Critical':
                        await self.request_additional_info(event['location'])
                else:
                    print(f"  ℹ️  Low severity - logging only")
                    
                print(f"{'─'*60}\n")
                
            except json.JSONDecodeError:
                print(f"[RESCUE] ⚠️  Failed to parse message body as JSON")
                
        async def request_additional_info(self, location):
            """Send REQUEST message for additional information"""
            request_body = {
                "request_type": "status_update",
                "location": location,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            request_msg = Message(
                to=str(self.agent.jid),
                sender=str(self.agent.jid),
                body=json.dumps(request_body),
                metadata={
                    "performative": "request",
                    "ontology": "disaster-response",
                    "role": "rescue-to-sensor"
                }
            )
            request_msg.set_metadata("performative", "request")
            request_msg.set_metadata("role", "rescue-to-sensor")
            
            await self.send(request_msg)
            
            log_message(
                direction="OUTGOING REQUEST MESSAGE (Rescue → Sensor)",
                sender="RescueBehavior",
                receiver="SensorBehavior",
                performative="REQUEST",
                content=f"Requesting detailed status update for {location}"
            )
            
    async def setup(self):
        """Setup both sensor and rescue behaviors"""
        self.rescue_responses = 0
        
        # Add sensor behavior (periodic detection)
        sensor = self.SensorBehaviour(period=7)
        self.add_behaviour(sensor)
        
        # Add rescue behavior (continuous message receiver)
        rescue = self.RescueBehaviour()
        self.add_behaviour(rescue)


# ═══════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════

async def main():
    """Start agent with both sensor and rescue behaviors"""
    
    # Clear previous message log
    with open('message_log.txt', 'w') as f:
        f.write("="*60 + "\n")
        f.write("LAB 4: AGENT COMMUNICATION MESSAGE LOG\n")
        f.write("FIPA-ACL Message Exchange - Disaster Response System\n")
        f.write("="*60 + "\n\n")
    
    # Use existing account from Labs 1-3
    agent_jid = "basicagent1@xmpp.jp"
    agent_password = "password123"
    
    print("\n" + "="*60)
    print("LAB 4: AGENT COMMUNICATION USING FIPA-ACL")
    print("="*60)
    print("\nDemonstrating INFORM and REQUEST performatives")
    print("Sensor behavior → Rescue behavior communication\n")
    
    agent = CommunicationDemoAgent(agent_jid, agent_password)
    await agent.start()
    
    print("\n✓ Agent running with Sensor and Rescue behaviors")
    print("  → Sensor detects disasters and sends INFORM messages")
    print("  → Rescue receives messages and triggers actions")
    print("  → REQUEST messages sent for critical events")
    print("\nPress Ctrl+C to stop\n")
    
    # Run for 45 seconds to capture multiple message exchanges
    try:
        await asyncio.sleep(45)
    except KeyboardInterrupt:
        print("\n\nStopping agent...")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"COMMUNICATION SUMMARY")
    print(f"{'='*60}")
    print(f"Rescue operations triggered: {agent.rescue_responses}")
    print(f"Message log saved to: message_log.txt")
    print(f"{'='*60}\n")
    
    await agent.stop()
    print("✓ Agent stopped.")


if __name__ == "__main__":
    asyncio.run(main())
