# Work-infra fleet ops (servers A–F + NAS)

All standing topology lives in `~/work/infra/docs/inventory.md` — read it before touching anything; update it after any topology change (user expects the doc to match reality). SSH aliases: `web-main` (A, hub), `crbsit-main` (C), `crbsit-standby` (D), `primepilot-main` (E), `primepilot-standby` (F) — all as `ldolgirev`; `nas` (host kbbs-X99M-H, user `kbbs`, kbbs IS in the docker group — docker work there needs no sudo).

## Access model

- No root passwords, ever. Where repeated root work is needed, hand Leonid a narrow NOPASSWD sudoers block to install as `/etc/sudoers.d/ldolgirev-firewall` (chmod 440, verify with `visudo -c`). Keep the command list minimal per need (e.g. nft/ufw/iptables + specific `systemctl …` units + `fail2ban-client`). He pastes it under root and reports back.
- `sudo -n <cmd>` failing with 'a password is required' means that server has no sudoers for ldolgirev yet — stage files in `/tmp` and hand him the install command instead of asking for passwords.
- `ping` from servers fails as non-root (`Operation not permitted`, missing cap_net_raw). Verify connectivity with `timeout 5 bash -c "echo > /dev/tcp/<ip>/<port>"` instead.

## Firewall / fail2ban baseline

- Etalon configs: `~/work/infra/deploy/host-baseline/` (`sshd/`, `fail2ban/jail.d/service.conf`, `apply-sshd-fail2ban.sh`). fail2ban etalon: sshd jail, action nftables, maxretry 10 / findtime 3600 / bantime 86400. Apply by staging the file to the server and `install -m 700 /tmp/service.conf /etc/fail2ban/jail.d/service.conf && systemctl restart fail2ban`.
- A fail2ban service can be `active` with ZERO jails: Debian default `jail.conf` ships `enabled = false` and a servers's `jail.d/service.conf` can exist but be EMPTY. 'installed + running' proves nothing — check `sudo fail2ban-client status sshd` returns a jail before declaring coverage.
- PITFALL: `systemctl is-active ufw` can read `inactive` while the rules are fully loaded and enforced — report firewall state from `sudo ufw status verbose`, never from the systemd unit state alone. Declaring a live firewall 'off' based on the unit state burns trust and can trigger unnecessary ruleset work.
- sshd baseline (all servers): PasswordAuthentication no, PermitRootLogin no, PubkeyAuthentication yes — set via `/etc/ssh/sshd_config.d/00-no-root-password.conf`.

## WireGuard mesh (hub-and-spoke, 10.0.0.0/24)

- Hub = A (10.0.0.1, 51820/udp, config `/etc/wireguard/wg0.conf`, one [Peer] block per node). Each spoke gets a fixed 10.0.0.x/32; the letter↔IP table is in the inventory.
- Adding a NAT'd node (e.g. the NAS behind a home router): no static IP needed. The new node gets `Endpoint = <hub>:51820` + `PersistentKeepalive = 25` and initiates; on the hub side add the peer WITHOUT an Endpoint (learned from the first handshake). Generate keypairs with python `cryptography` X25519 (raw 32 bytes, base64) — wg CLI isn't on macOS.
- PITFALL (hub-and-spoke cryptokey routing): a spoke's peer entry for the hub with `AllowedIPs = 10.0.0.1/32` makes it DROP forwarded packets sourced from other mesh IPs. For any new mesh node to reach spokes (or vice versa) two things must happen: hub forwards (`sudo ufw route allow in on wg0 out on wg0` + `net.ipv4.ip_forward=1`) AND every spoke's hub-peer AllowedIPs widened to `10.0.0.0/24` (`wg set wg0 peer <hub-pub> allowed-ips 10.0.0.0/24` + same change persisted in wg0.conf). Until both are done, spoke↔spoke (and new-node→spoke) traffic fails while hub↔node pings fine — the partial success is misleading.
- Kuma monitors split accordingly: internet-domain URLs work from anywhere; `http(s)://10.0.0.x` monitors only work once the above is complete. Test each direction before declaring the mesh whole.

## Uptime Kuma (two instances by design)

- Instance 1: docker on A, port 3001, ufw ALLOW only from 10.0.0.0/24 (DENY public). Instance 2: docker on NAS `uptime-kuma`, volume `uptime-kuma`, bound to BOTH `10.0.0.4:3001` (mesh) and `100.69.213.39:3001` (Tailscale, how Leonid browses from his Mac) — never 0.0.0.0.
- Shared credentials WITHOUT handling plaintext passwords: copy the `user` table rows (bcrypt hashes) from the source `kuma.db` into the target. Full-clone (users + monitors + settings + history) = stop target container, `docker cp` the source kuma.db over the target's, start. Both instances use image `louislam/uptime-kuma:1`.
- Push-type monitors (`push`, e.g. host/disk/load/memory) can only ever receive pushes on ONE instance — servers push to A. On the NAS clone they will show down forever; pause them there rather than debugging them.

## Fleet backups (restic → NAS) — implemented 2026-10-22

- Governed by the `nas-backup-ops` skill; plan `~/work/infra/docs/backup-nas-plan.md`, restore runbook `/srv/nas/backups/RESTORE.md` (+ copy `~/work/infra/docs/RESTORE-nas-backup.md`). Nightly: staging on servers 01:30–02:30, NAS pull 02:40, freshness `/srv/nas/backups/status.json`. Restore-tested 2026-10-23 (SQL/volume/image/kuma.db all OK; full GitLab-tar drill pending).
