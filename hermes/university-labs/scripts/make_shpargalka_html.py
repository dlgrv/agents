#!/usr/bin/env python3
"""Markdown -> HTML шпаргалка для чтения с телефона (см. university-labs SKILL.md).

Usage: python3 make_shpargalka_html.py <input.md> [output.html]
Дизайн: липкое меню с якорями, контрастные плашки h1, только светлая тема.
"""
import html as html_mod
import os
import re
import sys


def inline(s: str) -> str:
    s = html_mod.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def md_to_html(text: str) -> str:
    lines = text.split("\n")
    out = []
    in_list = False
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-|:]+\|$", lines[i + 1] or ""):
            out.append("<table><thead><tr>")
            cells = [c.strip() for c in ln.strip("|").split("|")]
            out.append("".join(f"<th>{inline(c)}</th>" for c in cells))
            out.append("</tr></thead><tbody>")
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</tbody></table>")
            continue
        if ln.startswith("# "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h1>{inline(ln[2:])}</h1>")
        elif ln.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2>{inline(ln[3:])}</h2>")
        elif ln.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(ln[2:])}</li>")
        elif ln.strip() == "---":
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<hr>")
        elif ln.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{inline(ln)}</p>")
        i += 1
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


STYLE = """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 16px;
    font: 16px/1.55 -apple-system, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    background: #fff; color: #1a1a1a; -webkit-text-size-adjust: 100%; }
  h1 { font-size: 1.25rem; line-height: 1.3; margin: 2.2em 0 0.6em;
    padding: 0.55em 0.75em; background: #1a1a1a; color: #fff; border-radius: 10px; }
  h1:first-child { margin-top: 0; }
  h2 { font-size: 1.05rem; margin: 1.6em 0 0.4em; color: #0a5;
    padding-bottom: 0.25em; border-bottom: 2px solid #0a5; }
  p { margin: 0.5em 0; }
  ul { margin: 0.4em 0; padding-left: 1.3em; }
  li { margin: 0.45em 0; }
  li::marker { color: #0a5; }
  table { width: 100%; border-collapse: collapse; margin: 0.8em 0; font-size: 0.88rem; }
  th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; vertical-align: top; }
  th { background: #f0f0f0; }
  td:first-child { white-space: nowrap; }
  code { font-family: ui-monospace, Menlo, monospace; font-size: 0.85em;
    background: #f0f0f0; padding: 1px 5px; border-radius: 4px; }
  hr { border: none; border-top: 1px solid #ddd; margin: 1.8em 0; }
  strong { color: #000; }
  em { color: #444; }
  .nav { position: sticky; top: 0; z-index: 10; display: flex; gap: 6px; flex-wrap: wrap;
    padding: 8px 0; margin: -16px -0 12px; background: #fff; border-bottom: 1px solid #eee; }
  .nav a { font-size: 0.8rem; text-decoration: none; padding: 5px 10px; border-radius: 999px;
    background: #f0f0f0; color: #1a1a1a; }
  .nav a:active { background: #0a5; color: #fff; }
"""


def build(md_path: str, out_path: str, nav_items) -> None:
    body = md_to_html(open(md_path, encoding="utf-8").read())
    nav = "\n".join(f'  <a href="#{anchor}">{label}</a>' for anchor, label in nav_items)
    doc = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{os.path.basename(md_path).rsplit(".", 1)[0]}</title>
<style>{STYLE}</style>
</head>
<body>
<nav class="nav">
{nav}
</nav>
{body}
</body>
</html>'''
    open(out_path, "w", encoding="utf-8").write(doc)


if __name__ == "__main__":
    md_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else md_path.rsplit(".", 1)[0] + ".html"
    # Якоря: h1, начинающиеся с 'ЛР<N.' -> id lr<N>; 'Если спросят' -> why.
    text = open(md_path, encoding="utf-8").read()
    anchors = []
    for m in re.finditer(r"^# (.+)$", text, re.M):
        t = m.group(1)
        mm = re.match(r"ЛР(\d+)", t)
        if mm:
            anchors.append((f"lr{mm.group(1)}", f"ЛР{mm.group(1)}"))
        elif t.startswith("Если спросят"):
            anchors.append(("why", "Почему так"))
    build(md_path, out_path, anchors)
    # Проставляем id на h1 пост-фактом.
    doc = open(out_path, encoding="utf-8").read()
    for anchor, label in anchors:
        doc = doc.replace(f"<h1>{label}", f'<h1 id="{anchor}">{label}', 1)
    open(out_path, "w", encoding="utf-8").write(doc)
    print(out_path, os.path.getsize(out_path), "bytes")
