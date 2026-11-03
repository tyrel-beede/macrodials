"""Turn the Markdown export of the article's source document into the site's post.

Usage: python tools/make_post.py <exported.md> <docs/blog/posts/target.md>

The export is the document as the Docs tool renders it: an H1 title, a byline line (date · author),
a release-stamp line, then the body. This script drops the byline and stamp (the post carries them in
front matter and its own footer), adds the blog front matter and the excerpt marker, converts each
table listed in TABLES into the site's image-plus-text pattern (the table stays in the post as the
text version; tools/site_tables.py renders the image at build time), and appends the release stamp.
"""
import re, sys, pathlib

FRONT = """---
date:
  created: 2026-11-02
  updated: {updated}
categories:
  - Articles
card: better-together-than-alone
kicker: Article · snapshot as of the Nov 2, 2026 close
card_foot: Version {version} · {released_short}
description: The physics, the money and the cycle behind a SpaceX–Tesla machine — a snapshot as of the Nov 2, 2026 close.
---

"""

# (first line of the table, image name, image title, subtitle)
TABLES = [
    ("| Per megawatt in orbit | Area | Mass |", "orbital-physics", "Orbital compute: the physics baseline per megawatt",
     "Stefan–Boltzmann at 300–340 K with emissivity 0.9; 1,361 W/m², 30% cells with 15% packing and degradation losses; NVL72-class racks of ~130 kW and ~1.4 t; Starship 150–200 t to low orbit. Order-of-magnitude baselines, not estimates for any vehicle."),
    ("| When | Test | What it decides |", "dated-tests", "The tests have dates",
     "The dated tests that confirm or falsify the thesis, in the order the evidence arrives. Times are U.S. market convention; 'NET' means no earlier than."),
]

STAMP = ("*Version {version} — verified and released {released}; source document revision {rev}. "
         "[Download the PDF](../../files/{pdf}){{ .release-link }}*{{ .release-stamp }}\n")


def main(src, dst, version="1.0", released="Nov 3, 2026, 11:40 MST", rev="196", pdf="Better_Together_Than_Alone_v1.0.pdf", updated="2026-11-03"):
    md = pathlib.Path(src).read_text(encoding="utf-8")
    lines = md.split("\n")
    assert lines[0].startswith("# "), "export should start with the H1 title"
    title = lines[0]
    i = 1
    # drop blank lines, the byline (date · author) and the release-stamp line that follow the title
    while i < len(lines) and (lines[i].strip() == "" or ("·" in lines[i] and "@" in lines[i]) or lines[i].startswith("*Version ")):
        i += 1
    body = "\n".join(lines[i:]).lstrip("\n")
    first_break = body.find("\n\n")
    body = body[:first_break] + "\n\n<!-- more -->" + body[first_break:]
    for first_line, name, alt, sub in TABLES:
        a = body.index(first_line)
        b = a
        while b < len(body):
            k = body.find("\n", b)
            line = body[b:k if k != -1 else len(body)]
            if not line.startswith("|"):
                break
            b = (k + 1) if k != -1 else len(body)
        table = body[a:b].rstrip("\n")
        indented = "\n".join("    " + l for l in table.split("\n"))
        block = (f"[![{alt}](images/{name}.png){{ .tbl }}](images/{name}.png)\n"
                 f"<!-- subtitle: {sub} -->\n\n"
                 f'??? note "Text version (selectable)"\n{indented}\n')
        body = body[:a] + block + body[b:]
    post = FRONT.format(updated=updated, version=version, released_short=released.split(",")[0] + "," + released.split(",")[1]) + title + "\n\n" + body.rstrip("\n") + "\n\n" + STAMP.format(version=version, released=released, rev=rev, pdf=pdf)
    pathlib.Path(dst).write_text(post, encoding="utf-8")
    print("wrote", dst, len(post), "chars; tables converted:", len(TABLES))


if __name__ == "__main__":
    main(*sys.argv[1:])
