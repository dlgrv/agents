# Test Code Verification Guide

This reference provides strategies for verifying that test codes correspond to the correct test content, preventing ordering errors and ensuring accurate pricing research.

## Why Code Verification Matters

Test codes don't always match their expected content:
- **Code 090016 vs 090013:** Both relate to Gamma-GT but may represent different test variants or methodologies
- **Regional code variations:** Same test may have different codes in different regions
- **Legacy vs current codes:** Some providers maintain multiple code versions
- **Test method differences:** Code may indicate testing method (ELISA vs LC-MS/MS) rather than the analyte

## Verification Strategies

### 1. Cross-Reference with Test Page Content

Always verify codes against the actual test page content:

```python
# Example: Verify GGT code matches test content
url = "https://www.cmd-online.ru/analizy-i-tseny/katalog-analizov/msk/gamma-glutamiltransferaza-ggt-gamma-glutamiltranspeptidaza-gamma-gluta/"
h = fetch_with_bot(url)

# Extract title and code from page
title = extract_title(h)  # Should contain "Гамма-глутамилтрансфераза"
code = extract_code(h)    # Should be 090016

# Verify match
if "Гамма-глутамилтрансфераза" in title and code == "090016":
    print("Code verified: correct Gamma-GT test")
else:
    print("Code mismatch - investigate further")
```

### 2. Check for Duplicate or Similar Codes

Search for multiple codes that might refer to similar tests:

- **Gamma-GT variants:** Look for codes like 090013, 090016, 300045
- **Vitamin D variants:** 080006 (standard ELISA), 080007 (total), advanced method codes
- **Thyroid variants:** Different codes for TSH, free T3, free T4

### 3. Use Provider Search Functionality

Many providers have search endpoints that accept both names and codes:

```python
# Example: Invitro search by code
search_url = "https://www.invitro.ru/golk/tests/api/v1/tests/by-article?article=090016&cityID=f1c3c4f0-3426-4cda-8449-e5d326e02f97"
response = urllib.request.urlopen(search_url)
data = json.loads(response.read().decode('utf-8'))

# Verify response contains expected test
if data.get('title') and 'Гамма' in data['title']:
    print(f"Code verified: {data['title']} ({data['price']} руб.)")
else:
    print("Code mismatch or test not found")
```

### 4. Step-by-Step Verification Process

For any test code you encounter:

1. **Find the test page** using the code in the URL
2. **Extract the test title** from the page content
3. **Compare with expected test name** (e.g., "Гамма-глутамилтрансфераза")
4. **If mismatch:** Search for alternative codes or contact support
5. **Document findings** for future reference

## Common Code Pitfalls

### Gamma-GT (GGT)
- **CMD:** 090016 = "Гамма-глутамилтрансфераза" (correct)
- **Avoid:** 090013 may be a different variant or outdated code
- **Verification:** Always check the test page title for exact match

### Vitamin D
- **CMD:** 080006 = standard ELISA method (2175 руб.)
- **CMD:** 080007 = total vitamin D (may include different methodology)
- **Avoid:** Advanced LC-MS/MS codes unless specifically required

### Thyroid Tests
- **TSH:** Usually single code (e.g., 060001 in CMD)
- **T3/T4:** May have separate codes from TSH
- **Panels:** Verify panel includes all required individual tests

### Blood Chemistry Bundles
- **Gemotest:** "Biokhimia 13" code varies by provider
- **CMD:** "Biokhimia 8" code 300338 (call to verify current availability)

## Best Practices

1. **Always verify codes against test page content** before reporting
2. **Search for similar codes** to ensure you have the correct one
3. **Use provider APIs** when available for code-to-test mapping
4. **Document the verification process** for transparency
5. **Double-check critical tests** (e.g., cancer markers, hormones)
6. **Be aware of regional code variations** when comparing across cities

## Red Flags

- Codes that don't appear in the provider's public catalog
- Codes with ambiguous or generic descriptions
- Multiple codes for seemingly identical tests
- Codes that redirect to unrelated test pages

When any red flag appears, contact provider support or use alternative verification methods.
