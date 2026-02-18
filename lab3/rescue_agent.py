"""
Lab 3: Goals, Events, and Reactive Behavior
DCIT 403 – Designing Intelligent Agent
Disaster Response & Relief Coordination System

This module implements a RescueAgent with FSM-based reactive behavior
that responds to disaster events detected by a simulated SensorAgent.

Goals:
  - Rescue Goal: Detect disasters and deploy rescue operations
  - Response Goal: Assess severity and allocate appropriate resources

FSM States:
  MONITORING -> ALERT_RECEIVED -> ASSESSING -> DISPATCHING -> RESPONDING -> MONITORING
"""

import asyncio
import random
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, PeriodicBehaviour

# Import the disaster environment from Lab 2
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lab2'))
from disaster_environment import DisasterEnvironment

# ─── FSM State Constants ───
STATE_MONITORING = "MONITORING"
STATE_ALERT_RECEIVED = "ALERT_RECEIVED"
STATE_ASSESSING = "ASSESSING"
STATE_DISPATCHING = "DISPATCHING"
STATE_RESPONDING = "RESPONDING"


# ═══════════════════════════════════════════════════════════════════
# FSM States
# ═══════════════════════════════════════════════════════════════════

class MonitoringState(State):
    """Agent monitors the environment for disaster events."""

    async def run(self):
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] STATE: MONITORING")
        print(f"{'='*60}")

        environment = self.agent.environment
        conditions = environment.get_environmental_conditions()

        print(f"  Temperature: {conditions['temperature']}°C")
        print(f"  Wind Speed : {conditions['wind_speed']} km/h")
        print(f"  Visibility : {conditions['visibility']}")
        print(f"  Access     : {conditions['accessibility']}")

        # Simulate event detection (40% chance)
        if random.random() < 0.4:
            event = environment.generate_disaster_event()
            self.agent.current_event = event
            print(f"\n  ** DISASTER EVENT DETECTED **")
            print(f"     Type     : {event['type']}")
            print(f"     Location : {event['location']}")
            print(f"     Severity : {event['severity']}")
            self.set_next_state(STATE_ALERT_RECEIVED)
        else:
            print(f"\n  [STATUS] All clear — no disaster detected.")
            # Small delay before next monitoring cycle
            await asyncio.sleep(3)
            self.set_next_state(STATE_MONITORING)


class AlertReceivedState(State):
    """An alert has been received from the environment / sensor."""

    async def run(self):
        event = self.agent.current_event
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] STATE: ALERT_RECEIVED")
        print(f"{'='*60}")
        print(f"  Alert: {event['type']} at {event['location']}")
        print(f"  Severity: {event['severity']} | Casualties: {event['casualties']}")
        print(f"  Resources needed: {event['resources_needed']}")

        # Log the event
        self.agent.event_log.append(event)

        await asyncio.sleep(1)
        self.set_next_state(STATE_ASSESSING)


class AssessingState(State):
    """Agent evaluates the severity and decides whether to dispatch."""

    async def run(self):
        event = self.agent.current_event
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] STATE: ASSESSING")
        print(f"{'='*60}")
        print(f"  Evaluating severity of {event['type']} at {event['location']}...")

        severity = event['severity']

        if severity in ('Medium', 'High', 'Critical'):
            print(f"  >> Severity '{severity}' requires dispatch.")
            await asyncio.sleep(1)
            self.set_next_state(STATE_DISPATCHING)
        else:
            print(f"  >> Severity '{severity}' is low — logging and resuming monitoring.")
            await asyncio.sleep(1)
            self.set_next_state(STATE_MONITORING)


class DispatchingState(State):
    """Agent dispatches rescue resources for the disaster event."""

    async def run(self):
        event = self.agent.current_event
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] STATE: DISPATCHING")
        print(f"{'='*60}")
        print(f"  Dispatching rescue team to {event['location']}...")
        print(f"  Disaster type : {event['type']}")
        print(f"  Severity      : {event['severity']}")
        print(f"  Resource type : {event['resources_needed']}")

        # Simulate dispatch delay
        await asyncio.sleep(2)
        print(f"  >> Rescue team deployed successfully.")
        self.set_next_state(STATE_RESPONDING)


class RespondingState(State):
    """Agent is actively responding to the disaster."""

    async def run(self):
        event = self.agent.current_event
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] STATE: RESPONDING")
        print(f"{'='*60}")
        print(f"  Rescue operation in progress at {event['location']}...")
        print(f"  Addressing {event['type']} — Severity: {event['severity']}")
        print(f"  Attending to {event['casualties']} estimated casualties.")

        # Simulate response duration
        await asyncio.sleep(3)
        print(f"  >> Response complete. Returning to monitoring.")
        self.agent.responses_completed += 1
        self.set_next_state(STATE_MONITORING)


# ═══════════════════════════════════════════════════════════════════
# Rescue Agent with FSM Behaviour
# ═══════════════════════════════════════════════════════════════════

class RescueAgent(Agent):
    """
    A reactive rescue agent that uses an FSM to respond to disaster events.

    Goals:
      1. Rescue Goal — Detect and react to disaster events
      2. Response Goal — Assess severity and deploy resources accordingly
    """

    async def setup(self):
        print(f"\nRescueAgent {self.jid} initializing...")

        # Shared state
        self.environment = DisasterEnvironment()
        self.current_event = None
        self.event_log = []
        self.responses_completed = 0

        # ── Build FSM ──
        fsm = FSMBehaviour()

        # Add states
        fsm.add_state(name=STATE_MONITORING,      state=MonitoringState(),      initial=True)
        fsm.add_state(name=STATE_ALERT_RECEIVED,   state=AlertReceivedState())
        fsm.add_state(name=STATE_ASSESSING,         state=AssessingState())
        fsm.add_state(name=STATE_DISPATCHING,       state=DispatchingState())
        fsm.add_state(name=STATE_RESPONDING,        state=RespondingState())

        # Add transitions
        fsm.add_transition(source=STATE_MONITORING,      dest=STATE_MONITORING)
        fsm.add_transition(source=STATE_MONITORING,      dest=STATE_ALERT_RECEIVED)
        fsm.add_transition(source=STATE_ALERT_RECEIVED,  dest=STATE_ASSESSING)
        fsm.add_transition(source=STATE_ASSESSING,       dest=STATE_DISPATCHING)
        fsm.add_transition(source=STATE_ASSESSING,       dest=STATE_MONITORING)
        fsm.add_transition(source=STATE_DISPATCHING,     dest=STATE_RESPONDING)
        fsm.add_transition(source=STATE_RESPONDING,      dest=STATE_MONITORING)

        self.add_behaviour(fsm)
        print(f"RescueAgent FSM behaviour added.\n")


# ═══════════════════════════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════════════════════════

async def main():
    # XMPP credentials (same remote server used in Lab 1 & Lab 2)
    agent_jid = "basicagent1@xmpp.jp"
    agent_password = "password123"

    agent = RescueAgent(agent_jid, agent_password)
    await agent.start()

    print("RescueAgent is running. Monitoring for disasters...")
    print("Press Ctrl+C to stop.\n")

    # Run for ~45 seconds to capture several FSM cycles
    try:
        await asyncio.sleep(45)
    except KeyboardInterrupt:
        print("\nStopping agent...")

    # ── Print execution summary ──
    print(f"\n{'='*60}")
    print(f"EXECUTION TRACE SUMMARY")
    print(f"{'='*60}")
    print(f"Total events detected : {len(agent.event_log)}")
    print(f"Responses completed   : {agent.responses_completed}")
    for i, evt in enumerate(agent.event_log, 1):
        print(f"\n  Event {i}:")
        print(f"    Timestamp : {evt['timestamp']}")
        print(f"    Type      : {evt['type']}")
        print(f"    Location  : {evt['location']}")
        print(f"    Severity  : {evt['severity']}")
        print(f"    Casualties: {evt['casualties']}")
        print(f"    Resources : {evt['resources_needed']}")
    print(f"{'='*60}\n")

    await agent.stop()
    print("RescueAgent stopped.")


if __name__ == "__main__":
    asyncio.run(main())
