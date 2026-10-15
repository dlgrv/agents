#!/usr/bin/env python3
"""
Browser-based recovery for JS-challenged pages.

Use when archives fail and the page serves a JavaScript challenge script
that requires execution to set cookies and deliver content.

Usage:
    python3 scripts/browser_recovery.py URL [--wait N] [--out FILE]

Exit codes: 0 success, 1 failure, 2 bad invocation.
"""
import argparse
import json
import re
import sys
import time
from urllib.parse import urlparse

# Titles that mean "this is still a challenge page, not content".
INTERSTITIAL_TITLES = (
    "just a moment",
    "redirecting",
    "google search",
    "attention required",
    "access denied",
    "are you a robot",
    "one more step",
    "checking your browser",
)

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def _page_title(body: bytes) -> str:
    m = TITLE_RE.search(body[:65536].decode("utf-8", "replace"))
    return re.sub(r"\s+", " ", m.group(1)).strip().lower() if m else ""


def is_interstitial(body: bytes) -> bool:
    """Return True if body is an interstitial, not real content."""
    title = _page_title(body)
    for marker in INTERSTITIAL_TITLES:
        if marker in title:
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Browser-based recovery for JS-challenged pages."
    )
    ap.add_argument("url")
    ap.add_argument("--wait", type=int, default=6, help="seconds to wait after navigation")
    ap.add_argument("--out", help="write recovered body to this file")
    ap.add_argument("--json", action="store_true", help="print metadata as JSON")
    args = ap.parse_args()

    if not args.url.startswith(("http://", "https://")):
        print("error: URL must start with http:// or https://", file=sys.stderr)
        return 2

    # Import browser helpers only when needed
    try:
        from browser_helpers import new_tab, wait_for_load, page_info, js
    except ImportError:
        print(
            "error: browser_helpers not available. Make sure browser tools are loaded.",
            file=sys.stderr,
        )
        return 2

    # Navigate and wait for challenge completion
    new_tab(args.url)
    time.sleep(args.wait)
    wait_for_load()

    # Check if we got the real page or an interstitial
    try:
        body_bytes = js("document.documentElement.outerHTML").encode("utf-8", "replace")
    except Exception as e:
        print(f"error: could not retrieve page content: {e}", file=sys.stderr)
        return 1

    if is_interstitial(body_bytes):
        print(
            "error: JS challenge still active after waiting. Page may require human interaction,"
            " or the challenge time is longer than the wait period.",
            file=sys.stderr,
        )
        return 1

    # Success! Extract metadata and save
    result = {
        "route": "browser",
        "provenance": "live",
        "snapshot_timestamp": None,
        "source_url": args.url,
        "body_bytes": len(body_bytes),
    }

    if args.out:
        with open(args.out, "wb") as fh:
            fh.write(body_bytes)
        result["saved_to"] = args.out

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
        if not args.out:
            print("\n--- body (first 2000 chars) ---")
            print(body_bytes[:2000].decode("utf-8", "replace"))

    return 0


if __name__ == "__main__":
    sys.exit(main())
