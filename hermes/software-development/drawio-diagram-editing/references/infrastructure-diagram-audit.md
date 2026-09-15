# Infrastructure Diagram Audit Checklist

Use this checklist when editing infrastructure/architecture diagrams in draw.io to ensure completeness and accuracy.

## Critical Elements to Verify

### 1. Topology Representation
- [ ] All servers/nodes are present and correctly labeled
- [ ] Network connections show correct traffic flows
- [ ] Load balancers and HA pairs clearly marked
- [ ] Dependencies between components explicit

### 2. Security Boundaries
- [ ] WireGuard or VPN mesh clearly marked (blue badge/label)
- [ ] Internal vs external traffic boundaries distinguished
- [ ] Firewall rules or security groups shown where relevant
- [ ] Encryption indicators for sensitive data flows

### 3. High Availability Features
- [ ] Primary/secondary relationships labeled
- [ ] Failover arrows show direction of failover
- [ ] Health check mechanisms indicated
- [ ] Quorum formations (etcd, Patroni) explicitly shown

### 4. Data Synchronization
- [ ] Database replication arrows show direction and type
- [ ] Backup storage targets clearly marked
- [ ] Sync frequency or RPO indicated
- [ ] Disaster recovery paths shown

### 5. Monitoring and Observability
- [ ] Monitoring system endpoints (Prometheus, Grafana)
- [ ] Alerting paths and notification channels
- [ ] Log aggregation and storage
- [ ] Health status indicators

## Common Infrastructure Patterns

### Web Service HA Pair
```
Client → DNS → Load Balancer → [Server A (Primary)] ↔ [Server B (Secondary)]
                           ↓              ↓
                       Database Replication
```

### Database Cluster with Patroni
```
etcd-1 ─┐
etcd-2 ─┼─ Patroni Manager
etcd-3 ─┘
    ↓
[Postgres Primary] ←→ [Postgres Replica]
    ↑                    ↑
Patroni Agent      Patroni Agent
```

### Backup Architecture
```
[Production Servers] → [NAS Backup Storage] → [Offsite/Cloud]
    ↓                    ↓                    ↓
  Daily Dumps      Age Encryption        Weekly Sync
```

### WireGuard Mesh
```
[Server A] ── wg0 ─→ [Server B]
  ↓                    ↓
[Server C] ── wg0 ─→ [Server D]
```

## Audit Questions

### Topology
1. Does the diagram match the actual infrastructure deployment?
2. Are all network connections bidirectional where needed?
3. Are single points of failure clearly marked?
4. Is the DNS routing accurately represented?

### Security
1. Are all internal communications secured (WireGuard, TLS)?
2. Are external-facing services isolated from internal services?
3. Are backup and monitoring systems on separate networks?
4. Are there any unencrypted data flows across security boundaries?

### Availability
1. Does every critical service have a failover mechanism?
2. Are quorum requirements met for distributed systems?
3. Are health checks and failover timeouts documented?
4. Can the infrastructure survive multiple simultaneous failures?

### Data
1. Are all databases replicated appropriately?
2. Are backups stored in a separate location?
3. Is data encryption at rest and in transit shown?
4. Are retention policies and backup frequencies indicated?

## Red Flags

- Single points of failure without mitigation
- Unclear or missing failover paths
- Unencrypted sensitive data flows
- Inconsistent HA patterns across similar services
- Missing monitoring or alerting
- No disaster recovery strategy
- Network loops or ambiguous routing

## Best Practices

### Diagram Clarity
- Use consistent color coding (e.g., blue for security, green for HA, orange for backup)
- Group related components with containers or boundaries
- Label all connections with protocols and ports
- Include IP addresses or ranges where relevant
- Use dashed lines for backup/async flows, solid for real-time

### Documentation Integration
- Cross-reference with runbooks and playbooks
- Include version control for diagram changes
- Link to configuration management code
- Reference monitoring dashboards and alert configurations

### Maintenance
- Review diagrams quarterly or after major changes
- Keep diagrams in version control alongside infrastructure code
- Use automated tools to validate diagrams against actual infrastructure
- Update diagrams when services are added or removed