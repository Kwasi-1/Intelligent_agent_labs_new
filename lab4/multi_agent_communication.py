"""
Lab 4: Agent Communication Using FIPA-ACL (Multi-Agent Version)
Real communication between separate SensorAgent and RescueAgent
"""

import asyncio
import json
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lab2'))
from disaster_environment import DisasterEnvironment


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
    
    with open('multi_agent_log.txt', 'a') as f:
        f.write(log_entry + '\n')


class SensorAgent(Agent):
    """Monitors environment and sends INFORM messages"""
    
    class DetectionBehaviour(PeriodicBehaviour):
        
        async def on_start(self):
            print(f"\n{'*'*60}")
            print(f"[SENSOR] {self.agent.jid} starting detection...")
            print(f"{'*'*60}\n")
            self.environment = DisasterEnvironment()
            self.detection_count = 0
            
        async def run(self):
            self.detection_count += 1
            print(f"\n[SENSOR] Detection Cycle {self.detection_count}")
            
            conditions = self.environment.get_environmental_conditions()
            print(f"[SENSOR] Monitoring: Temp={conditions['temperature']}°C, "
                  f"Wind={conditions['wind_speed']}km/h")
            
            import random
            if random.random() < 0.6:  # 60% chance
                event = self.environment.generate_disaster_event()
                print(f"[SENSOR] 🚨 DISASTER: {event['type']} at {event['location']} - {event['severity']}")
                await self.send_disaster_inform(event)
            else:
                print("[SENSOR] ✓ All clear")
                
        async def send_disaster_inform(self, event):
            msg = Message(
                to=self.agent.rescue_jid,
                sender=str(self.agent.jid),
                body=json.dumps(event),
                metadata={"performative": "inform", "ontology": "disaster-response"}
            )
            msg.set_metadata("performative", "inform")
            await self.send(msg)
            
            log_message(
                direction=">>> SENSOR SENDS INFORM >>>",
                sender=str(self.agent.jid),
                receiver=self.agent.rescue_jid,
                performative="INFORM",
                content=f"{event['type']} | {event['location']} | {event['severity']} | "
                        f"{event['casualties']} casualties | Needs: {event['resources_needed']}"
            )
            
    async def setup(self):
        self.rescue_jid = "kwasirescueagent1@xmpp.jp"
        self.add_behaviour(self.DetectionBehaviour(period=6))


class RescueAgent(Agent):
    """Receives INFORM messages and triggers rescue operations"""
    
    class MessageReceiverBehaviour(CyclicBehaviour):
        
        async def on_start(self):
            print(f"\n{'*'*60}")
            print(f"[RESCUE] {self.agent.jid} listening for alerts...")
            print(f"{'*'*60}\n")
            self.agent.responses = 0
            
        async def run(self):
            msg = await self.receive(timeout=10)
            
            if msg:
                performative = msg.get_metadata("performative")
                
                log_message(
                    direction="<<< RESCUE RECEIVES MESSAGE <<<",
                    sender=str(msg.sender),
                    receiver=str(self.agent.jid),
                    performative=performative.upper() if performative else "UNKNOWN",
                    content=msg.body[:200]
                )
                
                if performative == "inform":
                    await self.handle_inform(msg)
                    
        async def handle_inform(self, msg):
            try:
                event = json.loads(msg.body)
                
                print(f"\n{'─'*60}")
                print(f"[RESCUE] Processing alert from {msg.sender}")
                print(f"  Type: {event['type']} | Location: {event['location']}")
                print(f"  Severity: {event['severity']} | Casualties: {event['casualties']}")
                
                if event['severity'] in ('Medium', 'High', 'Critical'):
                    print(f"  🚁 DEPLOYING to {event['location']}")
                    print(f"  📦 Resources: {event['resources_needed']}")
                    self.agent.responses += 1
                else:
                    print(f"  ℹ️  Low severity - logged only")
                    
                print(f"{'─'*60}\n")
                
            except json.JSONDecodeError:
                print(f"[RESCUE] ⚠️ Failed to parse message")
                
    async def setup(self):
        self.responses = 0
        self.add_behaviour(self.MessageReceiverBehaviour())


async def main():
    # Clear log
    with open('multi_agent_log.txt', 'w') as f:
        f.write("="*60 + "\n")
        f.write("LAB 4: MULTI-AGENT FIPA-ACL COMMUNICATION LOG\n")
        f.write("="*60 + "\n\n")
    
    sensor_jid = "kwasisensoragent1@xmpp.jp"
    sensor_password = "sensor123"
    rescue_jid = "kwasirescueagent1@xmpp.jp"
    rescue_password = "rescue123"
    
    print("\n" + "="*60)
    print("LAB 4: MULTI-AGENT FIPA-ACL COMMUNICATION")
    print("="*60)
    print(f"\nSensorAgent: {sensor_jid}")
    print(f"RescueAgent: {rescue_jid}\n")
    
    rescue_agent = RescueAgent(rescue_jid, rescue_password)
    sensor_agent = SensorAgent(sensor_jid, sensor_password)
    
    await rescue_agent.start(auto_register=True)
    await asyncio.sleep(2)
    await sensor_agent.start(auto_register=True)
    
    print("✓ Both agents running. Waiting for messages...\n")
    
    # Run for 30 seconds
    try:
        await asyncio.sleep(30)
    except KeyboardInterrupt:
        print("\n\nStopping...")
    
    print(f"\n{'='*60}")
    print(f"COMMUNICATION SUMMARY")
    print(f"{'='*60}")
    print(f"Rescue operations: {rescue_agent.responses}")
    print(f"Log file: multi_agent_log.txt")
    print(f"{'='*60}\n")
    
    await sensor_agent.stop()
    await rescue_agent.stop()
    print("✓ Agents stopped.")

if __name__ == "__main__":
    asyncio.run(main())
