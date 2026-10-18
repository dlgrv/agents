#!/usr/bin/env python3
"""Fetch and parse GitHub trending pages (no official API exists).

Usage:
  trending.py repos [--since daily|weekly|monthly] [--lang LANG]
  trending.py developers [--since daily|weekly|monthly]

Prints a markdown table to stdout.
"""
import argparse
import html
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def repos(since: str, lang: str | None):
    base = f"https://github.com/trending/{lang}" if lang else "https://github.com/trending"
    src = fetch(f"{base}?since={since}")
    arts = re.findall(r'<article class="Box-row">(.*?)</article>', src, re.S)
    for a in arts:
        h2 = re.search(r"<h2[^>]*>(.*?)</h2>", a, re.S).group(1)
        repo = re.search(r'href="/([^"]+)"', h2).group(1)
        desc = re.search(r'<p class="col-9[^"]*">\s*(.*?)\s*</p>', a, re.S)
        lang_m = re.search(r'itemprop="programmingLanguage">([^<]+)<', a)
        total = re.search(r'href="/([^"]+)/stargazers".*?</svg>\s*([\d,]+)', a, re.S)
        week = re.search(r"([\d,]+) stars this (?:week|month)", a) or re.search(r"([\d,]+) stars today", a)
        yield [
            f"[{repo}](https://github.com/{repo})",
            lang_m.group(1) if lang_m else "-",
            total.group(2) if total else "?",
            week.group(1) if week else "?",
            (strip_tags(desc.group(1))[:100] if desc else ""),
        ]


def developers(since: str):
    src = fetch(f"https://github.com/trending/developers?since={since}")
    arts = re.findall(
        r'<article class="Box-row d-flex"[^>]*id="pa-[^"]*">(.*?)</article>', src, re.S
    )
    for a in arts:
        login = re.search(r'alt="@([^"]+)"', a).group(1)
        name = re.search(r"<h1[^>]*>\s*<a[^>]*>([^<]+)</a>", a).group(1).strip()
        repo = re.search(r'click_target&quot;:&quot;REPOSITORY&quot;.*?href="/([^"]+)"', a, re.S)
        repo_name = repo.group(1) if repo else "-"
        yield [
            f"[@{login}](https://github.com/{login}) ({name})",
            f"[{repo_name}](https://github.com/{repo_name})" if repo_name != "-" else "-",
        ]


def table(rows: list[list[str]], header: list[str]) -> None:
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join("---" for _ in header) + "|")
    for r in rows:
        print("| " + " | ".join(r) + " |")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=["repos", "developers"])
    p.add_argument("--since", default="weekly", choices=["daily", "weekly", "monthly"])
    p.add_argument("--lang", default=None, help="language filter for repos mode, e.g. python")
    args = p.parse_args()
    if args.mode == "repos":
        table(
            list(repos(args.since, args.lang)),
            ["Repo", "Language", "Stars", f"Stars {args.since}", "Description"],
        )
    else:
        table(list(developers(args.since)), ["Developer", "Popular repo"])


if __name__ == "__main__":
    main()
