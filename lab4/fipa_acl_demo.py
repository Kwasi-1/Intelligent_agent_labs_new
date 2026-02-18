"""
Lab 4: FIPA-ACL Communication Examples
Supplementary demonstration of INFORM and REQUEST performatives
"""

import asyncio
import json
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message


class DemoAgent(Agent):
    """Agent that demonstrates FIPA-ACL message exchange"""
    
    class SenderBehaviour(OneShotBehaviour):
        """Sends example INFORM and REQUEST messages"""
        
        async def run(self):
            print("\n" + "="*60)
            print("DEMONSTRATING FIPA-ACL PERFORMATIVES")
            print("="*60 + "\n")
            
            # Wait for receiver to be ready
            await asyncio.sleep(2)
            
            # 1. Send INFORM message
            print("1. Sending INFORM message...")
            inform_msg = Message(
                to=str(self.agent.jid),
                sender=str(self.agent.jid),
                body=json.dumps({
                    "type": "Earthquake",
                    "location": "Zone C",
                    "severity": "Critical",
                    "casualties": 50,
                    "resources_needed": "Medical"
                }),
                metadata={
                    "performative": "inform",
                    "ontology": "disaster-response",
                    "language": "JSON"
                }
            )
            inform_msg.set_metadata("performative", "inform")
            inform_msg.set_metadata("message_type", "disaster_alert")
            await self.send(inform_msg)
            
            self.log_message("INFORM", inform_msg)
            
            await asyncio.sleep(3)
            
            # 2. Send REQUEST message
            print("\n2. Sending REQUEST message...")
            request_msg = Message(
                to=str(self.agent.jid),
                sender=str(self.agent.jid),
                body=json.dumps({
                    "request_type": "status_update",
                    "location": "Zone C",
                    "details_needed": ["casualties", "resource_availability", "access_routes"]
                }),
                metadata={
                    "performative": "request",
                    "ontology": "disaster-response",
                    "language": "JSON"
                }
            )
            request_msg.set_metadata("performative", "request")
            request_msg.set_metadata("message_type", "info_request")
            await self.send(request_msg)
            
            self.log_message("REQUEST", request_msg)
            
        def log_message(self, performative, msg):
            """Log message details"""
            print(f"\n{'─'*60}")
            print(f"MESSAGE SENT")
            print(f"{'─'*60}")
            print(f"  Performative: {performative}")
            print(f"  From: {msg.sender}")
            print(f"  To: {msg.to}")
            print(f"  Ontology: {msg.get_metadata('ontology')}")
            print(f"  Body: {msg.body}")
            print(f"{'─'*60}\n")
            
            # Append to log file
            with open('fipa_acl_examples.txt', 'a') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"FIPA-ACL {performative} MESSAGE\n")
                f.write(f"{'='*60}\n")
                f.write(f"Timestamp   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"From        : {msg.sender}\n")
                f.write(f"To          : {msg.to}\n")
                f.write(f"Performative: {performative}\n")
                f.write(f"Ontology    : {msg.get_metadata('ontology')}\n")
                f.write(f"Language    : {msg.get_metadata('language')}\n")
                f.write(f"Body        :\n{json.dumps(json.loads(msg.body), indent=2)}\n")
                f.write(f"{'='*60}\n")
    
    
    class ReceiverBehaviour(CyclicBehaviour):
        """Receives and processes messages"""
        
        async def on_start(self):
            print("\n[RECEIVER] Ready to receive messages...\n")
            self.received_count = 0
            
        async def run(self):
            msg = await self.receive(timeout=10)
            
            if msg:
                self.received_count += 1
                performative = msg.get_metadata("performative")
                message_type = msg.get_metadata("message_type")
                
                print(f"\n{'='*60}")
                print(f"MESSAGE RECEIVED #{self.received_count}")
                print(f"{'='*60}")
                print(f"  Performative: {performative.upper()}")
                print(f"  Message Type: {message_type}")
                print(f"  From: {msg.sender}")
                
                if performative == "inform":
                    data = json.loads(msg.body)
                    print(f"\n  [INFORM] Disaster Alert Received:")
                    print(f"    Type: {data['type']}")
                    print(f"    Location: {data['location']}")
                    print(f"    Severity: {data['severity']}")
                    print(f"\n  → Action: Processing disaster alert...")
                    
                elif performative == "request":
                    data = json.loads(msg.body)
                    print(f"\n  [REQUEST] Information Request Received:")
                    print(f"    Request Type: {data['request_type']}")
                    print(f"    Location: {data['location']}")
                    print(f"    Details Needed: {', '.join(data['details_needed'])}")
                    print(f"\n  → Action: Gathering requested information...")
                    
                print(f"{'='*60}\n")
                
    async def setup(self):
        # Clear log file
        with open('fipa_acl_examples.txt', 'w') as f:
            f.write("="*60 + "\n")
            f.write("LAB 4: FIPA-ACL MESSAGE EXAMPLES\n")
            f.write("="*60 + "\n")
        
        self.add_behaviour(self.ReceiverBehaviour())
        self.add_behaviour(self.SenderBehaviour())


async def main():
    agent_jid = "basicagent1@xmpp.jp"
    agent_password = "password123"
    
    print("\n" + "="*60)
    print("LAB 4: FIPA-ACL PERFORMATIVES DEMONSTRATION")
    print("="*60)
    
    agent = DemoAgent(agent_jid, agent_password)
    await agent.start()
    
    # Run for 10 seconds
    await asyncio.sleep(10)
    
    print(f"\n{'='*60}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'='*60}")
    print("Message examples saved to: fipa_acl_examples.txt\n")
    
    await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
