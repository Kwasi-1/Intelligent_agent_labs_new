# Lab 4: Agent Communication Using FIPA-ACL

## Objective
Enable inter-agent communication using FIPA-ACL performatives for disaster response coordination.

## Implementation Overview

Lab 4 implements FIPA-ACL (Foundation for Intelligent Physical Agents - Agent Communication Language) message exchange between agents in the disaster response system.

## Files

| File | Description |
|------|-------------|
| `multi_agent_communication.py` | ⭐ **Real multi-agent FIPA-ACL communication** (separate agents) |
| `communication_demo.py` | Single-agent demo with Sensor and Rescue behaviors |
| `fipa_acl_demo.py` | Simplified demonstration of INFORM and REQUEST messages |
| `multi_agent_log.txt` | ⭐ **Log from real multi-agent communication** |
| `message_log.txt` | Log from single-agent demo |
| `fipa_acl_examples.txt` | Formatted examples of FIPA-ACL messages |
| `test_connection.py` | XMPP account connectivity test utility |

## FIPA-ACL Performatives Implemented

### 1. INFORM
**Purpose:** Agent notifies another agent of a fact or observation

**Example Use Case:** SensorAgent informs RescueAgent about detected disaster

```json
{
  "performative": "inform",
  "ontology": "disaster-response",
  "body": {
    "type": "Earthquake",
    "location": "Zone C",
    "severity": "Critical",
    "casualties": 50,
    "resources_needed": "Medical"
  }
}
```

### 2. REQUEST
**Purpose:** Agent requests information or action from another agent

**Example Use Case:** RescueAgent requests detailed status update from SensorAgent

```json
{
  "performative": "request",
  "ontology": "disaster-response",
  "body": {
    "request_type": "status_update",
    "location": "Zone C",
    "details_needed": ["casualties", "resource_availability", "access_routes"]
  }
}
```

## Agent Behaviors

### SensorBehaviour
- Periodically monitors environment using `DisasterEnvironment` (from Lab 2)
- Detects disasters (fire, flood, earthquake, storm)
- Sends **INFORM** messages to RescueAgent with disaster details
- Message contains: type, location, severity, casualties, resources needed

### RescueBehaviour
- Continuously listens for incoming messages
- Receives **INFORM** messages from SensorAgent
- Parses message content (JSON format)
- Triggers actions based on disaster severity:
  - **Low:** Log only
  - **Medium/High/Critical:** Deploy rescue team and allocate resources
- Sends **REQUEST** messages for Critical events to get additional information

## Message Flow

### Multi-Agent Communication (True Distributed System)
```
┌──────────────────────┐                              ┌──────────────────────┐
│  SensorAgent         │   INFORM (disaster alert)    │  RescueAgent         │
│  kwasisensoragent1   │ ──────────────────────────>  │  kwasirescueagent1   │
│  @xmpp.jp            │                              │  @xmpp.jp            │
│                      │   REQUEST (status update)    │                      │
│  - Detects disasters │ <────────────────────────────│  - Receives alerts   │
│  - Sends INFORM msgs │                              │  - Triggers actions  │
└──────────────────────┘                              └──────────────────────┘
         ↑                                                        ↓
         └────────── Remote XMPP Server (xmpp.jp) ──────────────┘
```

**Key Features:**
- 🌐 Two separate agent processes communicating over XMPP
- 📨 True asynchronous message passing
- 🔐 Authenticated connections to remote server
- 📊 Each agent has its own JID and behaviors

### Single-Agent Demo (Internal Communication)
```
┌──────────────┐                                    ┌──────────────┐
│              │   INFORM (disaster detected)       │              │
│ SensorAgent  │ ─────────────────────────────────> │ RescueAgent  │
│              │                                    │              │
│              │   REQUEST (status update)          │              │
│              │ <───────────────────────────────── │              │
└──────────────┘                                    └──────────────┘
```

## Execution

### ⭐ Run Multi-Agent Communication (Recommended)
**True multi-agent FIPA-ACL communication between separate agents**
```bash
cd lab4
python multi_agent_communication.py
```

**XMPP Accounts Used:**
- SensorAgent: `kwasisensoragent1@xmpp.jp`
- RescueAgent: `kwasirescueagent1@xmpp.jp`

**Output:**
- Real-time message exchange between two separate agents
- Console display showing INFORM messages sent and received
- `multi_agent_log.txt` with complete bidirectional communication log
- Summary of rescue operations triggered

### Run Single-Agent Demo
```bash
cd lab4
python communication_demo.py
```

**Output:**
- Console display of sensor detections and rescue actions
- `message_log.txt` with complete message exchange log
- Summary of rescue operations triggered

### Run FIPA-ACL Examples
```bash
python fipa_acl_demo.py
```

**Output:**
- Clear demonstration of INFORM and REQUEST messages
- `fipa_acl_examples.txt` with formatted message details

## Message Structure

All messages follow SPADE's Message format with FIPA-ACL metadata:

```python
msg = Message(
    to="receiver@xmpp.jp",
    sender="sender@xmpp.jp",
    body=json.dumps(content),
    metadata={
        "performative": "inform",  # or "request"
        "ontology": "disaster-response",
        "language": "JSON"
    }
)
```

## Deliverables

✅ **Message Logs**
- ⭐ `multi_agent_log.txt` - **Real multi-agent FIPA-ACL communication log**
- `message_log.txt` - Single-agent demo message log
- `fipa_acl_examples.txt` - Structured examples of both performatives

✅ **Agent Communication Code**
- ⭐ `multi_agent_communication.py` - **True multi-agent system with separate agents**
- `communication_demo.py` - Single-agent demonstration
- `fipa_acl_demo.py` - Clear demonstration of FIPA-ACL performatives

✅ **Practical Tasks Completed**
1. ✅ Implemented ACL message exchange between agents
2. ✅ Used INFORM and REQUEST performatives
3. ✅ Parsed incoming messages and triggered agent actions

## Key Concepts Demonstrated

- **FIPA-ACL Performatives:** INFORM and REQUEST
- **Message Parsing:** JSON format for structured data exchange
- **Event-Driven Actions:** Messages trigger rescue operations
- **Ontology:** Disaster response domain knowledge
- **Asynchronous Communication:** Non-blocking message exchange

## Integration with Previous Labs

- **Lab 2:** Reuses `DisasterEnvironment` for event generation
- **Lab 3:** Builds on reactive behavior concepts
- **Future Labs:** Message exchange forms foundation for multi-agent coordination

## Notes

- Uses remote XMPP server (xmpp.jp) for agent communication
- **Multi-agent version** uses separate XMPP accounts:
  - `kwasisensoragent1@xmpp.jp` (SensorAgent)
  - `kwasirescueagent1@xmpp.jp` (RescueAgent)
- Single-agent demo uses one account with multiple behaviors
- Messages logged with timestamps for execution trace analysis
- JSON format enables structured data exchange between agents
- Auto-registration enabled for seamless account setup
