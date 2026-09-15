---
name: multi-agent-a2a-orchestration
description: "Set up equal peer Hermes agents via A2A."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, a2a, orchestration, peer-to-peer, networking, distributed, tailscale, shared-memory]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [hermes-agent, computer-use]
---

# Multi-Agent A2A Orchestration

## Overview

This skill provides the workflow for setting up a network of equal Hermes agents that can communicate and delegate tasks to each other using the A2A (Agent-to-Agent) protocol. Agents run as independent peers on different machines and coordinate directly, without a central controller.

## Architecture

```
[Mac Agent]  <-->  [Server Agent]
   (peer)            (peer)
      |                 |
[Shared Memory (Honcho)]
```

Each agent:
- Runs its own Hermes gateway
- Listens on A2A port (default 9900)
- Exposes an Agent Card for discovery
- Can call other agents using `a2a_call`
- Shares memory via Honcho

## Quick Start

### Prerequisites

- Tailscale installed and logged in on all machines
- SSH access between machines (for setup)
- Hermes installed on all machines
- Firewall rules allowing A2A port (9900) on tailnet

### Step 1: Tailscale Setup

Ensure all machines are on the same tailnet:

```bash
# On each machine
tailscale status
tailscale up
```

### Step 2: Configure A2A on Each Agent

Add to `~/.hermes/.env` on each machine:

```bash
# Enable A2A platform
echo 'gateway.platforms.a2a.enabled=true' >> ~/.hermes/.env

# Set A2A host to the machine's tailnet IP
echo 'A2A_HOST=<machine-tailnet-ip>' >> ~/.hermes/.env

# Set A2A port (default 9900)
echo 'A2A_PORT=9900' >> ~/.hermes/.env
```

### Step 3: Configure Peer Agents

On each machine, add the other agent as a peer in `~/.hermes/config.yaml`:

```yaml
a2a_agents:
  <peer-name>:
    url: "http://<peer-tailnet-ip>:9900"
    auth:
      type: bearer
      token: "<shared-secret-token>"
    timeout: 120
```

Generate a shared token and distribute it securely (use base64 encoding for safe copy-paste in chat).

### Step 4: Restart Gateways

```bash
hermes gateway restart
```

### Step 5: Test Connection

Verify Agent Cards are accessible:

```bash
curl -s http://<peer-tailnet-ip>:9900/.well-known/agent-card.json
```

## Detailed Workflow

### Tailscale Configuration

- Tailscale provides secure P2P networking between agents
- Agents discover each other via tailnet IPs
- P2P routing is automatic and optimized
- Use `tailscale ping <peer-ip>` to test connectivity

### A2A Protocol Configuration

- Always set `A2A_HOST` to the machine's tailnet IP
- Without `A2A_HOST`, A2A binds to localhost only (inaccessible from peers)
- Use bearer token authentication for secure cross-agent calls
- Set appropriate timeout (default 120s)

### Peer Token Management

Generate secure tokens:

```bash
# Generate a random token
token=$(openssl rand -base64 32 | tr -d '=+/' | cut -c1-32)
echo "A2A_PEER_TOKENS=$token"
```

Distribute tokens securely (base64 encoding in chat):

```bash
echo 'A2A_PEER_TOKENS=<token>' | base64
```

### Agent Discovery

Each agent exposes an Agent Card at `/.well-known/agent-card.json`:

```json
{
  "name": "agent-name",
  "description": "Hermes Agent — a general-purpose agent reachable over A2A.",
  "url": "http://<tailnet-ip>:9900/",
  "version": "1.0.0",
  "provider": {"organization": "Hermes Agent", "url": "http://<tailnet-ip>:9900/"}
}
```

### Cross-Agent Task Delegation

Use `a2a_call` to delegate tasks between agents:

```python
# In a tool or script
from hermes_tools import a2a_call

result = a2a_call(
    peer="<peer-name>",
    task="<task-description>",
    timeout=120
)
```

### Common Pitfalls

#### 1. A2A_HOST Not Set

**Symptom:** Agent doesn't respond on A2A port from peers

**Fix:** Always set `A2A_HOST=<tailnet-ip>` in `.env`

#### 2. Token Typos

**Symptom:** Authentication failures when calling peers

**Fix:** Verify tokens match exactly (use `grep` and `wc -c` to check length)

#### 3. Firewall Blocking

**Symptom:** Connection timeouts to peer A2A port

**Fix:** Check macOS firewall prompts; allow incoming connections for Python/hermes

#### 4. Gateway Not Restarted

**Symptom:** Configuration changes not taking effect

**Fix:** Always restart gateway after config changes: `hermes gateway restart`

### Troubleshooting

#### Check A2A Port Binding

```bash
lsof -iTCP:9900 -sTCP:LISTEN
```

#### Test Peer Connectivity

```bash
tailscale ping <peer-tailnet-ip>
nc -z -w 3 <peer-tailnet-ip> 9900
```

#### Verify Agent Card

```bash
curl -s http://<peer-tailnet-ip>:9900/.well-known/agent-card.json | head -c 200
```

#### Check Gateway Logs

```bash
tail -f ~/.hermes/logs/gateway.log | grep a2a
```

## Advanced Configuration

### Custom Ports

Change A2A port by setting:

```bash
echo 'A2A_PORT=9999' >> ~/.hermes/.env
```

### Multiple Peers

Add multiple agents to `config.yaml`:

```yaml
a2a_agents:
  server:
    url: "http://server-tailnet-ip:9900"
    auth:
      type: bearer
      token: "server-token"
  laptop:
    url: "http://laptop-tailnet-ip:9900"
    auth:
      type: bearer
      token: "laptop-token"
```

### Honcho Integration (Shared Memory)

Install and configure Honcho for shared memory between agents:

```bash
# Install Honcho
pip install honcho

# Configure in ~/.hermes/.env
echo 'MEMORY_PROVIDER=honcho' >> ~/.hermes/.env
echo 'HONCHO_URL=http://<honcho-server>:8080' >> ~/.hermes/.env
```

## Security Considerations

- Use unique tokens for each peer pair
- Rotate tokens periodically
- Restrict A2A access to tailnet only
- Monitor gateway logs for unauthorized access attempts
- Use HTTPS in production environments

## References

- [A2A Protocol Documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/a2a)
- [Tailscale Documentation](https://tailscale.com/kb/1018/install/)
- [Honcho Memory Provider](https://github.com/plastic-labs/honcho)
