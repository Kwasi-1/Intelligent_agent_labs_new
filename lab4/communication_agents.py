"""
Lab 4: Agent Communication Using FIPA-ACL
DCIT 403 – Designing Intelligent Agent
Disaster Response & Relief Coordination System

This module implements inter-agent communication using FIPA-ACL performatives.
- SensorAgent detects disasters and sends INFORM messages
- RescueAgent receives messages, parses them, and triggers actions
- CoordinatorAgent can send REQUEST messages for status updates

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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
# SENSOR AGENT - Detects disasters and sends INFORM messages
# ═══════════════════════════════════════════════════════════════════

class SensorAgent(Agent):
    """
    Monitors environment and sends INFORM messages when disasters are detected.
    """
    
    class DetectionBehaviour(PeriodicBehaviour):
        """Periodically detect disasters and inform rescue agents"""
        
        async def on_start(self):
            print(f"\n{'*'*60}")
            print(f"SensorAgent {self.agent.jid} starting...")
            print(f"{'*'*60}\n")
            self.environment = DisasterEnvironment()
            self.detection_count = 0
            
        async def run(self):
            """Detect disasters and send INFORM messages"""
            self.detection_count += 1
            
            print(f"\n--- Detection Cycle {self.detection_count} ---")
            
            # Get environmental conditions
            conditions = self.environment.get_environmental_conditions()
            print(f"Monitoring: Temp={conditions['temperature']}°C, "
                  f"Wind={conditions['wind_speed']}km/h, "
                  f"Visibility={conditions['visibility']}")
            
            # 40% chance of detecting a disaster
            import random
            if random.random() < 0.4:
                event = self.environment.generate_disaster_event()
                print(f"\n🚨 DISASTER DETECTED: {event['type']} at {event['location']}")
                
                # Send INFORM message to RescueAgent
                await self.send_disaster_inform(event)
            else:
                print("✓ All clear - no disaster detected")
                
        async def send_disaster_inform(self, event):
            """Send INFORM message about detected disaster"""
            msg = Message(
                to=self.agent.rescue_agent_jid,
                sender=str(self.agent.jid),
                body=json.dumps(event),
                metadata={
                    "performative": "inform",
                    "ontology": "disaster-response",
                    "language": "JSON"
                }
            )
            msg.set_metadata("performative", "inform")
            
            await self.send(msg)
            
            log_message(
                direction="OUTGOING MESSAGE",
                sender=str(self.agent.jid),
                receiver=self.agent.rescue_agent_jid,
                performative="INFORM",
                content=f"Disaster: {event['type']} | Location: {event['location']} | "
                        f"Severity: {event['severity']} | Casualties: {event['casualties']}"
            )
            
    async def setup(self):
        self.rescue_agent_jid = "kwasirescueagent1@xmpp.jp"
        behaviour = self.DetectionBehaviour(period=8)  # Check every 8 seconds
        self.add_behaviour(behaviour)


# ═══════════════════════════════════════════════════════════════════
# RESCUE AGENT - Receives messages and triggers actions
# ═══════════════════════════════════════════════════════════════════

class RescueAgent(Agent):
    """
    Receives INFORM messages about disasters and triggers rescue operations.
    Can send REQUEST messages to ask for status updates.
    """
    
    class MessageReceiverBehaviour(CyclicBehaviour):
        """Continuously listen for incoming messages"""
        
        async def on_start(self):
            print(f"\n{'*'*60}")
            print(f"RescueAgent {self.agent.jid} starting...")
            print(f"Listening for disaster alerts...")
            print(f"{'*'*60}\n")
            self.agent.responses = 0
            
        async def run(self):
            """Receive and process messages"""
            msg = await self.receive(timeout=10)
            
            if msg:
                performative = msg.get_metadata("performative")
                
                log_message(
                    direction="INCOMING MESSAGE",
                    sender=str(msg.sender),
                    receiver=str(self.agent.jid),
                    performative=performative.upper() if performative else "UNKNOWN",
                    content=msg.body[:200]  # Limit content length
                )
                
                # Parse and handle the message
                if performative == "inform":
                    await self.handle_inform(msg)
                elif performative == "request":
                    await self.handle_request(msg)
                else:
                    print(f"⚠️  Unknown performative: {performative}")
                    
        async def handle_inform(self, msg):
            """Handle INFORM messages about disasters"""
            try:
                event = json.loads(msg.body)
                
                print(f"\n{'─'*60}")
                print(f"[RescueAgent] Processing disaster alert...")
                print(f"  Type     : {event['type']}")
                print(f"  Location : {event['location']}")
                print(f"  Severity : {event['severity']}")
                print(f"  Casualties: {event['casualties']}")
                print(f"  Resources: {event['resources_needed']}")
                
                # Trigger action based on severity
                if event['severity'] in ('Medium', 'High', 'Critical'):
                    print(f"\n  🚁 ACTION: Deploying rescue team to {event['location']}")
                    print(f"  📦 Allocating resources: {event['resources_needed']}")
                    self.agent.responses += 1
                    
                    # Optionally send REQUEST to sensor for more info
                    if event['severity'] == 'Critical':
                        await self.request_additional_info(msg.sender, event['location'])
                else:
                    print(f"  ℹ️  Low severity - logging only")
                    
                print(f"{'─'*60}\n")
                
            except json.JSONDecodeError:
                print(f"⚠️  Failed to parse message body as JSON")
                
        async def request_additional_info(self, sensor_jid, location):
            """Send REQUEST message for additional information"""
            request_msg = Message(
                to=str(sensor_jid),
                sender=str(self.agent.jid),
                body=f"Request detailed status for {location}",
                metadata={
                    "performative": "request",
                    "ontology": "disaster-response"
                }
            )
            request_msg.set_metadata("performative", "request")
            
            await self.send(request_msg)
            
            log_message(
                direction="OUTGOING MESSAGE",
                sender=str(self.agent.jid),
                receiver=str(sensor_jid),
                performative="REQUEST",
                content=f"Requesting detailed status for {location}"
            )
            
        async def handle_request(self, msg):
            """Handle REQUEST messages (for future extension)"""
            print(f"\n[RescueAgent] Received REQUEST: {msg.body}")
            
    async def setup(self):
        behaviour = self.MessageReceiverBehaviour()
        self.add_behaviour(behaviour)


# ═══════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════

async def main():
    """Start both agents and enable communication"""
    
    # Clear previous message log
    with open('message_log.txt', 'w') as f:
        f.write("="*60 + "\n")
        f.write("LAB 4: AGENT COMMUNICATION MESSAGE LOG\n")
        f.write("FIPA-ACL Message Exchange - Disaster Response System\n")
        f.write("="*60 + "\n\n")
    
    # Agent credentials (using remote XMPP server)
    sensor_jid = "kwasisensoragent1@xmpp.jp"
    sensor_password = "sensor123"
    
    rescue_jid = "kwasirescueagent1@xmpp.jp"
    rescue_password = "rescue123"
    
    # Create and start agents
    print("\n" + "="*60)
    print("LAB 4: AGENT COMMUNICATION USING FIPA-ACL")
    print("="*60)
    
    sensor_agent = SensorAgent(sensor_jid, sensor_password)
    rescue_agent = RescueAgent(rescue_jid, rescue_password)
    
    await rescue_agent.start(auto_register=True)
    await asyncio.sleep(2)  # Let rescue agent initialize first
    await sensor_agent.start(auto_register=True)
    
    print("\n✓ Both agents are running and communicating...")
    print("  SensorAgent will detect disasters and send INFORM messages")
    print("  RescueAgent will receive messages and trigger actions")
    print("\nPress Ctrl+C to stop\n")
    
    # Run for 50 seconds to capture multiple message exchanges
    try:
        await asyncio.sleep(50)
    except KeyboardInterrupt:
        print("\n\nStopping agents...")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"COMMUNICATION SUMMARY")
    print(f"{'='*60}")
    print(f"Rescue responses triggered: {rescue_agent.responses}")
    print(f"Message log saved to: message_log.txt")
    print(f"{'='*60}\n")
    
    await sensor_agent.stop()
    await rescue_agent.stop()
    print("✓ All agents stopped.")


if __name__ == "__main__":
    asyncio.run(main())
