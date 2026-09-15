# Admin Brute-Force Protection Setup

When securing admin interfaces (GitLab, primebpm, primepilot admin) against password brute-force attacks, implement these layers in order:

## Layer 1: 2FA (Two-Factor Authentication)
**Priority: Critical** - Makes password guessing useless

### GitLab 2FA
```bash
# Enable 2FA for all users
sudo gitlab-rails console production
User.all.each { |u| u.update!(two_factor_enabled: true) }
exit

# Set policy: require 2FA for all users
sudo gitlab-rails console production
ApplicationSetting.current.update!(require_two_factor_authentication: true)
exit
```

### Custom Admin Apps (primebpm, primepilot)
- Use TOTP libraries (Google Authenticator compatible)
- Server-side: `pyotp` (Python), `rotp` (Ruby), etc.
- No internet required for verification
- Store secrets in environment variables or secure vault

### Implementation Time
- GitLab: 2-5 minutes
- Custom apps: 30-60 minutes per app

## Layer 2: fail2ban
**Priority: High** - Auto-ban after N failed attempts

### Installation
```bash
# Ubuntu/Debian
sudo apt install fail2ban

# CentOS/RHEL
sudo yum install fail2ban
```

### Configuration
Create `/etc/fail2ban/jail.d/admins.conf`:
```ini
[nginx-auth]
enabled  = true
port     = http,https
filter   = nginx-auth
logpath  = /var/log/nginx/error.log
maxretry = 5
findtime = 10m
bantime  = 1h

[gitlab-auth]
enabled  = true
port     = http,https
filter   = gitlab-auth
logpath  = /var/log/gitlab/gitlab-rails/application.log
maxretry = 3
findtime = 5m
bantime  = 30m
```

### Nginx Auth Filter
Create `/etc/fail2ban/filter.d/nginx-auth.conf`:
```ini
[Definition]
failregex = .*user .* authentication failure.*
            .*Invalid user.*
            .*user .* was not found*
ignoreregex =
```

### GitLab Auth Filter
Create `/etc/fail2ban/filter.d/gitlab-auth.conf`:
```ini
[Definition]
failregex = .*Failed authentication for .* from <HOST>
            .*Authentication failed for .* from <HOST>
ignoreregex =
```

### Start and Enable
```bash
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
sudo fail2ban-client reload
```

## Layer 3: Rate Limiting
**Priority: Medium** - Limits requests before they hit application

### Nginx Rate Limit
```nginx
# Global rate limit zone
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

# GitLab login path
location /users/sign_in {
    limit_req zone=login burst=3 nodelay;
    proxy_pass http://gitlab;
}

# Custom admin apps
location /admin {
    limit_req zone=login burst=2 nodelay;
    proxy_pass http://backend;
}
```

### Application-Level Rate Limit
If using Django/Flask/etc., implement rate limiting in middleware:
```python
# Django example
from django_ratelimit.decorators import ratelimit
from django.http import HttpResponse

@ratelimit(key='ip', rate='5/m', block=True)
def admin_login(request):
    # Login logic here
    pass
```

## Layer 4: Built-in Application Limits
**Priority: Low** - Additional protection within apps

### GitLab Built-in Limits
- Admin Area → Settings → Network → Rate limits
- Admin Area → Settings → Network → Failed login ban

### Custom Apps
- Implement account lockout after N failed attempts
- Use exponential backoff for repeated failures
- Log all failed attempts for monitoring

## Monitoring and Alerting

### Fail2ban Status
```bash
sudo fail2ban-client status nginx-auth
sudo fail2ban-client status gitlab-auth
```

### Log Monitoring
```bash
# Check recent bans
sudo journalctl -u fail2ban -f

# Check nginx auth failures
sudo tail -f /var/log/nginx/error.log | grep authentication
```

### Alerting Setup
```bash
# Simple email alert for bans
sudo apt install mailutils
sudo tee /etc/fail2ban/action.d/mail-whois.conf > /dev/null << 'EOF'
[Definition]
actionstart = printf %%b "Subject: [Fail2ban] <name> banned <ip> on `uname -n`\n\n`date`\n\nBan for <ip> has been issued by Fail2ban for jail <name>.\n\n" | mail -s "[Fail2ban] <name> banned <ip> on `uname -n`" recipient
actionstop = printf %%b "Subject: [Fail2ban] <name> banned <ip> on `uname -n`\n\n`date`\n\nBan for <ip> has been removed by Fail2ban for jail <name>.\n\n" | mail -s "[Fail2ban] <name> banned <ip> on `uname -n`" recipient
actioncheck =
actionban = printf %%b "Subject: [Fail2ban] <name> banned <ip> on `uname -n`\n\n`date`\n\nBan for <ip> has been issued by Fail2ban for jail <name>.\n\n" | mail -s "[Fail2ban] <name> banned <ip> on `uname -n`" recipient
actionunban = printf %%b "Subject: [Fail2ban] <name> banned <ip> on `uname -n`\n\n`date`\n\nBan for <ip> has been removed by Fail2ban for jail <name>.\n\n" | mail -s "[Fail2ban] <name> banned <ip> on `uname -n`" recipient
EOF

# Configure email recipient in jail.local
sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
action = %(action_)s
action_mwl = %(mail-whois[name])s
recipient = admin@example.com
EOF
```

## Testing

### Test Fail2ban
```bash
# Try to brute force (simulate)
curl -X POST http://your-server/users/sign_in -d "user=admin&password=wrong"
curl -X POST http://your-server/users/sign_in -d "user=admin&password=wrong"
curl -X POST http://your-server/users/sign_in -d "user=admin&password=wrong"
curl -X POST http://your-server/users/sign_in -d "user=admin&password=wrong"
curl -X POST http://your-server/users/sign_in -d "user=admin&password=wrong"

# Check if IP is banned
sudo fail2ban-client status nginx-auth
```

### Test Rate Limit
```bash
# Test rate limiting
for i in {1..10}; do curl -X POST http://your-server/users/sign_in; done
# Should get 429 after 5th request
```

## Rollback

If issues arise, disable temporarily:
```bash
sudo systemctl stop fail2ban
# Or disable specific jail
sudo fail2ban-client set nginx-auth unbanip YOUR_IP
```

## Maintenance

### Regular Checks
```bash
# Check fail2ban status
sudo fail2ban-client status

# Review logs for false positives
sudo grep "authentication failure" /var/log/nginx/error.log

# Update fail2ban rules
sudo fail2ban-client --reload
```

### Best Practices
- Test changes in staging first
- Monitor for false positives
- Keep fail2ban updated
- Review logs weekly
- Test recovery procedures

### Cost
- Layer 1 (2FA): $0 (built-in)
- Layer 2 (fail2ban): $0 (open source)
- Layer 3 (rate limit): $0 (nginx built-in)
- Layer 4 (app limits): $0 (built-in)

Total implementation time: 45-90 minutes
