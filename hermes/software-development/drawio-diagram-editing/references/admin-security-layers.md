# Admin Security Layers for Infrastructure Diagrams

When documenting admin panels (GitLab, primebpm, admin interfaces) in infrastructure diagrams, always include security annotations showing protection layers.

## Security Layer Annotations

### Recommended Security Measures
1. **2FA (Two-Factor Authentication)** - Always enabled for admin panels
2. **fail2ban** - Auto-ban after failed login attempts
3. **Rate Limiting** - Limit login requests per minute
4. **IP Restrictions** - Only allow from trusted networks (future goal)

### Visual Representation

Use colored badges and annotations to show security status:

- **Blue badge** at node top: "Protected by 2FA"
- **Red text** for admin nodes: "Admin Interface"
- **Small annotations** showing specific protections

### XML Pattern for Admin Nodes

```xml
<mxCell id="gitlab-admin" value="<div style=\"font-size:12px\">GitLab<br/><div style=\"color:red;font-weight:bold\">Admin</div></div>" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="120" height="60" as="geometry"/>
</mxCell>
<mxCell id="gitlab-security" value="<div style=\"font-size:10px;color:blue\">2FA + fail2ban + rate limit</div>" style="rounded=1;whiteSpace=wrap;html=1;points=[[0,0.5],[1,0.5]]" edge="1" source="gitlab-admin" target="gitlab-admin" parent="1">
  <mxGeometry x="100" y="280" width="120" height="20" as="geometry" relative="1" offset="0 0"/>
</mxCell>
```

### Common Admin Panel Locations

| Service | Typical Port | Security Priority |
|---------|-------------|------------------|
| GitLab | 80/443 | High (contains CI/CD) |
| primebpm | 8080 | Medium (business logic) |
| primepilot admin | 3000 | Low (internal tooling) |

### Integration with Infrastructure Audit

When using the infrastructure diagram audit checklist:

- [ ] Admin nodes clearly marked with "Admin" label
- [ ] Security annotations visible for all admin interfaces
- [ ] Protection layers documented (2FA, rate limiting, etc.)
- [ ] External access restrictions shown (if implemented)

### Pitfall: Missing Security Context
**Never show admin panels without security annotations.** Admin interfaces are prime targets for brute-force attacks and should always be documented with their protection mechanisms.

### Pitfall: Inconsistent Security Notation
**Use consistent color coding and placement for security badges.** All admin nodes should have the same visual style for security annotations to avoid confusion.

### Example: Complete Admin Node

```python
# GitLab admin with full security annotation
mxcell = ET.SubElement(mr, 'mxCell', {
    'id': 'gitlab-admin',
    'value': '<div style="font-size:12px">GitLab<br/><div style="color:red;font-weight:bold">Admin</div></div>',
    'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#D79B00;',
    'vertex': '1',
    'parent': '1'
})

# Security annotation badge
mxbadge = ET.SubElement(mr, 'mxCell', {
    'id': 'gitlab-security-badge',
    'value': '<div style="font-size:10px;color:white;background-color:#0066CC;padding:2px;border-radius:3px">2FA</div>',
    'style': 'rounded=1;whiteSpace=wrap;html=1;',
    'vertex': '1',
    'parent': '1'
})

# Position badge above main node
mxgeom_badge = ET.SubElement(mxbadge, 'mxGeometry', {
    'x': '100',
    'y': '180',  # Above main node
    'width': '50',
    'height': '20',
    'as': 'geometry'
})
```