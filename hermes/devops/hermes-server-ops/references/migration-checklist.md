# Hermes Server Migration Checklist

## Pre-migration
- [ ] Confirm new server IP and credentials
- [ ] Install Hermes on new server: `curl -fsSL https://get.hermesagent.com | bash`
- [ ] Start minimal gateway: `systemctl --user enable --now hermes-gateway`
- [ ] On old server: create backup: `tar -czf hermes-state-$(date +%Y%m%d-%H%M%S).tar.gz ~/.hermes`

## State Transfer
- [ ] Transfer backup: `scp hermes-state-*.tar.gz root@<NEW_IP>:/tmp`
- [ ] On new server: stop gateway: `systemctl --user stop hermes-gateway`
- [ ] Extract state: `tar -xzf /tmp/hermes-state-*.tar.gz -C ~/.hermes --strip-components=1`
- [ ] Restart gateway: `systemctl --user restart hermes-gateway`

## Post-migration Verification
- [ ] Server identity: `hostname` should match new IP
- [ ] SSH keys: `ls ~/.ssh/authorized_keys` should include user's key
- [ ] Provider test: `hermes -z "Ответь одним словом: работает?"` → Да
- [ ] Session count: `sqlite3 ~/.hermes/state.db "SELECT COUNT(*) FROM sessions"` should match old server
- [ ] Telegram polling: `grep -E 'telegram|polling|error' ~/.hermes/logs/gateway.log | tail -3`
- [ ] Dashboard port: `ss -tlnp 2>/dev/null | grep :9119` should show 0.0.0.0:9119
- [ ] Skills count: `ls ~/.hermes/skills/ | wc -l` should match expected
- [ ] No old processes: Only new server's hermes processes should be running

## User Connection
- [ ] Update SSH config on Mac to point to new IP
- [ ] Test desktop connection to new server
- [ ] Verify Telegram sessions continuity (old session titles appear in new list)

## Cleanup (optional)
- [ ] Confirm old server processes stopped
- [ ] Shut down old server
- [ ] Remove old server from SSH config
