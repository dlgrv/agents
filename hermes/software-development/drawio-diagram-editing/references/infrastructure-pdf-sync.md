# Infrastructure Diagram and PDF Synchronization

When working with infrastructure diagrams and PDF documentation, maintain strict synchronization between visual (.drawio) and textual (PDF) documentation to avoid drift.

## Synchronization Rules

### 1. Always Update Both Together
- Diagram (.drawio) and PDF documentation must be updated in the same session
- Use the same version control commit for both files
- Reference the diagram by page number in PDF text (e.g., "see page 2, diagram")

### 2. Document Changes in Both Formats
- **Diagram**: Show new nodes, connections, topology changes
- **PDF**: Update IP addresses, server roles, hardware specs, failover procedures
- **Cross-reference**: PDF should point to diagram sections and vice versa

### 3. Validation After Updates
- After diagram edits, render PNG and verify against PDF descriptions
- After PDF text edits, verify diagram still matches all described elements
- Check that all IPs, roles, and connections in PDF are present in diagram

## Common Synchronization Points

### Server Table Updates
When server IPs or hardware specs change:
1. Update XML node text in draw.io
2. Update server table in PDF
3. Verify connection paths still match

### Topology Changes
When adding/removing servers or connections:
1. Update XML connections and node positions
2. Update traffic flow descriptions in PDF
3. Update failover scenarios in PDF

### Security Boundaries
When WireGuard or ACLs change:
1. Update mesh badges and connection lines
2. Update security sections in PDF
3. Update port matrix in PDF

## Pitfalls to Avoid

### 1. IP Address Drift
**Always verify all IPs in PDF match diagram nodes.** Use grep or text search to cross-reference:
- Extract all IPs from PDF text
- Extract all IPs from diagram XML
- Compare lists and flag mismatches

### 2. Role Description Mismatch
**Server roles in PDF must exactly match diagram labels.** Common issues:
- Diagram shows "web main", PDF shows "web primary"
- Diagram shows "etcd1", PDF shows "judge 1"
- Use consistent terminology across both documents

### 3. Missing Connection References
**PDF must describe all major connections shown in diagram.** Check:
- Load balancer → server pairs
- Database replication arrows
- WireGuard mesh connections
- Backup storage links

### 4. Outdated Scenarios
**Failover scenarios in PDF must match diagram topology.** Verify:
- Primary/secondary relationships correct
- Failover paths match connections
- Quorum configurations accurate

## Synchronization Workflow

1. **Edit Diagram**
   - Make XML changes
   - Render PNG to verify layout
   - Note all changes made

2. **Update PDF**
   - Cross-reference diagram changes
   - Update all affected sections
   - Verify terminology consistency

3. **Validate Both**
   - Check IPs match
   - Check roles match
   - Check connections described
   - Check scenarios accurate

4. **Commit Together**
   - Same commit message for both files
   - Reference each other in commit

## Example Sync: Adding New Server

### Diagram Changes
- Add new node with correct IP and role
- Update connections to/from new node
- Adjust layout to avoid overlaps

### PDF Changes
- Add new server to server table
- Update traffic flow descriptions
- Update failover scenarios if applicable
- Update monitoring sections

### Validation
- Verify new IP appears in both documents
- Verify new connections described in PDF
- Verify no existing elements broken

## Automation Helpers

### IP Cross-Reference Script
```python
# Extract IPs from PDF
import re
with open('infra-best-practice.pdf', 'rb') as f:
    # Use PyPDF2 or similar to extract text
    pdf_text = f.read().decode('utf-8', errors='ignore')
    ips_pdf = re.findall(r'\b(?:10\.0\.0\.\d+|\d{1,3}\.\d{1,3}\.\d{3}\.\d{3})\b', pdf_text)

# Extract IPs from diagram
import xml.etree.ElementTree as ET
xml = open('selectel-infra.drawio').read()
root = ET.fromstring(xml)
texts = []
for cell in root.find('diagram').find('mxGraphModel').find('root').findall('mxCell'):
    value = cell.get('value') or ''
    ips = re.findall(r'\b(?:10\.0\.0\.\d+|\d{1,3}\.\d{1,3}\.\d{3}\.\d{3})\b', value)
    texts.extend(ips)

# Compare
print(f"PDF IPs: {set(ips_pdf)}")
print(f"Diagram IPs: {set(texts)}")
print(f"Mismatch: {set(ips_pdf) - set(texts)}")
```

### Terminology Consistency Check
```python
# Check for consistent role naming
roles_pdf = re.findall(r'(web|crbsit|primepilot) (?:основной|запасной|primary|secondary)', pdf_text, re.IGNORECASE)
roles_diagram = []
for cell in cells.values():
    value = cell.get('value') or ''
    if any(r in value.lower() for r in ['web', 'crbsit', 'primepilot']):
        roles_diagram.append(value)

print(f"PDF roles: {roles_pdf}")
print(f"Diagram roles: {roles_diagram}")
```