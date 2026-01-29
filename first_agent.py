import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class MyFirstAgent(Agent):
    class HelloBehaviour(CyclicBehaviour):
        async def run(self):
            print(f"Hello! I'm agent {self.agent.jid}")
            print("Agent is alive and running!")
            await asyncio.sleep(5)  # Wait 5 seconds
            await self.agent.stop()  # Stop after first run
    
    async def setup(self):
        print(f"Agent {self.jid} is starting...")
        hello = self.HelloBehaviour()
        self.add_behaviour(hello)
        print("Behaviour added. Agent is ready!")

async def main():
    # REPLACE THESE WITH YOUR ACTUAL CREDENTIALS
    jid = "basicagent1@xmpp.jp"  # Your XMPP account
    password = "password123"        # Your password
    
    agent = MyFirstAgent(jid, password)
    await agent.start()
    
    print("Agent started. Check output above...")
    
    # Wait for agent to finish
    while agent.is_alive():
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())