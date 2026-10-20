# WireGuard Mesh Setup (user's estate)

## Setup pattern for multi-DC HA
- **Subnet:** 10.0.0.0/24 (user's decision)
- **Nodes:** A=.1 (hub), D=.2, E=.3, NAS=.4, F=.6, C=.7
- **Always use vanilla WireGuard** (no custom forks; user rejected 'ru' variants).
- **No public etcd access** — all etcd/Patroni traffic only via WG mesh.
- **No public Patroni REST** — only from WG peers.

## Configuration
- **Postgres replication**: inside WG only
- **etcd cluster**: inside WG only
- **Patroni DCS**: inside WG only
- **NAS backups**: pull over WG (NAS SSHes out to each server — outbound from the NAS is unrestricted, so the "NAS ufw allows only 10.0.0.1" rule stays intact; do not propose opening NAS ufw to the mesh for backups)
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

## Adding a peer behind NAT / with a dynamic IP (validated)
Static public IP is needed on ONE side only — the hub. A spoke behind home
NAT / CGNAT / floating IP initiates the tunnel itself and keeps it open with
keepalive; the hub keys off the peer's public key, not its address:
- Spoke config: `Endpoint = <hub_ip>:51820` + `PersistentKeepalive = 25`;
  `AllowedIPs = 10.0.0.0/24` (mesh traffic only, never full-tunnel).
- Hub peer entry: NO `Endpoint` line — the hub learns the address from the
  first handshake packet and updates it automatically.
- Order of operations: add the peer on the hub first (`wg set wg0 peer ... allowed-ips 10.0.0.X/32`, then append the same Peer block to wg0.conf for persistence), then bring up the spoke — the handshake lands immediately.
- Keys for the whole exchange can be generated locally (python
  cryptography.hazmat.primitives.asymmetric.x25519 — LibreSSL's `openssl
  genpkey -algorithm X25519` may be unavailable on macOS) and handed to the
  user as ready-to-paste blocks; Leonid explicitly prefers commands with real
  values already substituted over templates with placeholders.

## Hub-and-spoke: spoke-to-spoke traffic is BLOCKED by default (validated fix)
With stock spoke configs (hub peer `AllowedIPs = 10.0.0.1/32`) a spoke drops
packets sourced from any other spoke's mesh IP, so a new node can reach only
the hub. Full connectivity = two changes, both required:
1. Hub: `sudo ufw route allow in on wg0 out on wg0` (allow forwarding inside
   the tunnel; also needs `net.ipv4.ip_forward=1`).
2. EVERY spoke: widen the hub peer's AllowedIPs from `10.0.0.1/32` to
   `10.0.0.0/24` — runtime `wg set wg0 peer <hub_pub> allowed-ips 10.0.0.0/24`
   AND persist with
   `sed -i '/^AllowedIPs = 10.0.0.1\/32/c\AllowedIPs = 10.0.0.0/24' /etc/wireguard/wg0.conf`
   (runtime alone dies at the next wg-quick restart).
- Never run the spoke `wg set` on the HUB itself with the hub's own public
  key — it creates a bogus self-peer with a /24 AllowedIPs; check
  `wg show wg0 peers` after a batch change and remove it
  (`wg set wg0 peer <hub_pub> remove`). The accompanying sed is harmless on
  the hub (its config has no 10.0.0.1/32 line).
- Verify the fix from the NEW node with unprivileged TCP probes to each
  spoke's real service port (80/22/...), then confirm the monitoring instance
  on that node goes green — heartbeats are the end-to-end proof.

## Verifying connectivity as a non-root user
`ping` fails for unprivileged users on hardened hosts (`ping: socket:
Operation not permitted` — missing cap_net_raw), and an unprivileged `ssh`
account usually cannot read `/etc/wireguard/` either. Verify instead with a
TCP probe that needs no capabilities:
```bash
ssh <host> 'timeout 5 bash -c "echo > /dev/tcp/10.0.0.X/22" && echo ok || echo fail'
```
Also `cat /proc/sys/net/ipv4/ip_forward` on the hub (readable without root)
to confirm spoke-to-spoke forwarding is even possible before debugging a
failing spoke→spoke path.

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