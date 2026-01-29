import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour

class MyBasicAgent(Agent):
    class MyBehaviour(OneShotBehaviour):
        async def run(self):
            print("Hello! I am a basic SPADE agent")
            print(f"My JID is: {self.agent.jid}")
            print("Agent is running successfully!")
            
            # Stop the agent after running
            await asyncio.sleep(2)
            await self.agent.stop()
    
    async def setup(self):
        print(f"Agent {self.jid} starting...")
        behaviour = self.MyBehaviour()
        self.add_behaviour(behaviour)

async def main():
    # Replace with your actual XMPP credentials
    agent_jid = "basicagent1@xmpp.jp"  # CHANGE THIS
    agent_password = "password123"      # CHANGE THIS
    
    agent = MyBasicAgent(agent_jid, agent_password)
    
    # Start the agent (await it properly)
    await agent.start()
    
    print("Agent is running. Press Ctrl+C to stop.")
    
    # Keep agent running for a while
    await asyncio.sleep(5)
    
    # Stop the agent
    await agent.stop()
    print("Agent finished execution")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())