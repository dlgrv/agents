# WireGuard Mesh Setup (user's estate)

## Setup pattern for multi-DC HA
- **Subnet:** 10.0.0.0/24 (user's decision)
- **Nodes:** A=.1, D=.2, E=.3, NAS=.4 (Selectel + PrimePilot + NAS)
- **Always use vanilla WireGuard** (no custom forks; user rejected 'ru' variants).
- **No public etcd access** — all etcd/Patroni traffic only via WG mesh.
- **No public Patroni REST** — only from WG peers.

## Configuration
- **Postgres replication**: inside WG only
- **etcd cluster**: inside WG only
- **Patroni DCS**: inside WG only
- **NAS backups**: rsync over WG
- **Admin panels**: only accessible via WG

## User preference
- User prefers vanilla WG over alternatives (e.g. nginx proxy).
- User prefers mesh over client-server for all internal services.
- User prefers no TLS over WG (no need for double encryption).
- User prefers simple key setup over complex PKI.

## Commands to run per server
```bash
# Generate keys
wg genkey | tee privatekey | wg pubkey > publickey

# Configure /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <server_private_key>
Address = 10.0.0.X/24
ListenPort = 51820

[Peer]
PublicKey = <peer_public_key>
AllowedIPs = 10.0.0.0/24
Endpoint = <peer_public_ip>:51820
PersistentKeepalive = 25
```

## Firewall (nftables)
```bash
nft add table inet filter
nft add chain inet filter input { type filter hook input priority 0 \; }
nft add rule inet filter input iifname != lo ct state new,untracked tcp dport 51820 accept
nft add rule inet filter input iifname != lo ct state new,untracked udp dport 51820 accept
nft add rule inet filter input iifname != lo ct state new,untracked tcp dport {5432,8008} accept
nft add rule inet filter input iifname != lo ct state new,untracked udp dport 2379 accept
nft add rule inet filter input iifname != lo ct state new,untracked udp dport 2380 accept
```