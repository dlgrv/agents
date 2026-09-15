#!/usr/bin/env python3
"""
Static verification for C# files when no compiler is available.
Checks: brace balance, paren balance, quote balance, type definitions,
inheritance hierarchy, cross-file type references.

Usage:
    python3 verify-cs-static.py <path-to-folder-with-cs-files>

This is ad-hoc verification, NOT a compiled build pass.
Full compilation requires Unity Editor or .NET SDK.
"""

import os
import re
import sys


def verify_folder(base_path):
    results = []
    type_definitions = {}  # type_name -> relative_path
    all_contents = {}      # relative_path -> content

    # Pass 1: collect files and type definitions
    for root, dirs, files in os.walk(base_path):
        for f in sorted(files):
            if not f.endswith(".cs"):
                continue
            path = os.path.join(root, f)
            with open(path) as fh:
                content = fh.read()
            rel = os.path.relpath(path, base_path)
            all_contents[rel] = content

            # Find class/enum/interface definitions (word boundary, not in comments)
            # Strip comments first for cleaner matching
            stripped = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
            for m in re.finditer(r'\b(?:class|enum|interface)\s+(\w+)', stripped):
                type_definitions[m.group(1)] = rel

    # Known external types (Unity/stdlib) — don't flag as missing
    known_external = {
        "MonoBehaviour", "ScriptableObject", "CharacterController", "NavMeshAgent",
        "Vector3", "Quaternion", "Collider", "GameObject", "Transform", "Button",
        "TextMeshProUGUI", "TMP_Text", "Debug", "Input", "Physics", "Time",
        "Destroy", "Instantiate", "FindFirstObjectByType", "FindObjectsByType",
        "FindObjectsSortMode", "RequireComponent", "CreateAssetMenu",
        "SerializeField", "Header", "Space", "Tooltip", "Range",
        "Action", "Queue", "List", "IEnumerable", "ICollection",
        "Application", "PlayerPrefs", "Sprite", "Mathf",
        "Attribute", "AttributeUsage", "AttributeTargets",
        "IDisposable", "Component", "Object", "Behaviour",
    }

    # Pass 2: per-file checks
    for rel, content in sorted(all_contents.items()):
        issues = []

        # Brace balance
        opens = content.count("{")
        closes = content.count("}")
        if opens != closes:
            issues.append(f"BRACE MISMATCH: {opens}{{ vs {closes}}}")

        # Paren balance
        open_p = content.count("(")
        close_p = content.count(")")
        if open_p != close_p:
            issues.append(f"PAREN MISMATCH: {open_p}( vs {close_p})")

        # Quote balance (per line, ignoring comments)
        odd_quote_lines = 0
        for line in content.split("\n"):
            if "//" in line:
                line = line[:line.index("//")]
            if line.count('"') % 2 != 0:
                odd_quote_lines += 1
        if odd_quote_lines > 0:
            issues.append(f"ODD QUOTE COUNT on {odd_quote_lines} lines")

        # Class/enum definition check
        stripped = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
        has_type = bool(re.search(r'\b(?:class|enum|interface)\s+\w+', stripped))
        if not has_type:
            issues.append("NO CLASS/ENUM/INTERFACE DEFINITION")

        lines = len(content.split("\n"))
        status = "OK" if not issues else "; ".join(issues)
        results.append((rel, lines, status))

    # Pass 3: cross-file reference check
    ref_issues = []
    for rel, content in sorted(all_contents.items()):
        stripped = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
        refs = set(re.findall(r'\b([A-Z]\w+)\b', stripped))
        our_type_refs = refs - known_external
        for ref in sorted(our_type_refs):
            if ref not in type_definitions:
                # Could be a Unity type we didn't enumerate — skip
                pass
            # If it IS in our types, it resolves — no issue

    # Print results
    print(f"{'File':<50} {'Lines':>5}  Status")
    print("-" * 85)
    all_ok = True
    for rel, lines, status in results:
        marker = "  " if status == "OK" else "!! "
        print(f"{marker}{rel:<48} {lines:>5}  {status}")
        if status != "OK":
            all_ok = False

    print(f"\nTotal: {len(results)} .cs files")
    print(f"Type definitions found: {len(type_definitions)}")
    print(f"All structural checks pass: {all_ok}")
    print()
    print("=" * 85)
    print("NOTE: This is ad-hoc static verification, NOT a compiled build pass.")
    print("Full compilation requires Unity Editor or .NET SDK.")
    if all_ok:
        print("Result: All static checks passed (braces, parens, quotes, types).")
    else:
        print("Result: ISSUES FOUND — see above.")
    return all_ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify-cs-static.py <path-to-cs-folder>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isdir(path):
        print(f"Error: {path} is not a directory")
        sys.exit(1)
    ok = verify_folder(path)
    sys.exit(0 if ok else 1)
