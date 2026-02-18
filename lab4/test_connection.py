"""Quick test of XMPP account connectivity"""
import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour

class TestAgent(Agent):
    class TestBehaviour(OneShotBehaviour):
        async def run(self):
            print(f"✓ Agent {self.agent.jid} connected successfully!")
            await asyncio.sleep(1)
            await self.agent.stop()
    
    async def setup(self):
        print(f"Starting {self.jid}...")
        self.add_behaviour(self.TestBehaviour())

async def main():
    print("Testing XMPP account connectivity...\n")
    
    # Test credentials
    accounts = [
        ("kwasisensoragent1@xmpp.jp", "sensor123", "SensorAgent"),
        ("kwasirescueagent1@xmpp.jp", "rescue123", "RescueAgent"),
    ]
    
    for jid, pwd, name in accounts:
        print(f"Testing {name} ({jid})...")
        try:
            agent = TestAgent(jid, pwd)
            await agent.start(auto_register=True)
            await asyncio.sleep(3)
            if agent.is_alive():
                print(f"  ✓ {name} connected successfully\n")
            await agent.stop()
        except Exception as e:
            print(f"  ✗ {name} failed: {e}\n")
    
    print("Connectivity test complete.")

if __name__ == "__main__":
    asyncio.run(main())
