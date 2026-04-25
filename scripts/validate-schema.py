#!/usr/bin/env python3
"""Validate Person JSON-LD blocks in rendered HTML.

Catches the class of bug that would ship structured data with a wrong
name, broken URL, malformed JSON, or a placeholder sameAs entry.
Structural-only — does not ping external URLs (LinkedIn returns 999 to
bots, so reachability checks would be flaky in CI).

Exits 0 if every JSON-LD block is well-formed and matches expected
identity invariants. Exits 1 with errors printed to stderr otherwise.

Run after `quarto render`. Reads from _site/.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# Identity invariants — change these if the canonical identity changes.
EXPECTED_NAME = "Michael P. Kerr"
EXPECTED_DOMAIN = "https://mpk15956.github.io/"
EXPECTED_CONTEXT = "https://schema.org"

JSONLD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL,
)


def validate_person(data, source):
    """Return a list of error strings for a Person JSON-LD block."""
    if data.get("@type") != "Person":
        return []  # not a Person block; nothing to validate here.

    errors = []
    if data.get("@context") != EXPECTED_CONTEXT:
        errors.append(
            f"{source}: @context is {data.get('@context')!r}, expected {EXPECTED_CONTEXT!r}"
        )
    if data.get("name") != EXPECTED_NAME:
        errors.append(
            f"{source}: name is {data.get('name')!r}, expected {EXPECTED_NAME!r}"
        )
    url = data.get("url", "")
    if not url.startswith(EXPECTED_DOMAIN):
        errors.append(f"{source}: url {url!r} should start with {EXPECTED_DOMAIN}")
    image = data.get("image", "")
    if image and not image.startswith(EXPECTED_DOMAIN):
        errors.append(f"{source}: image {image!r} should start with {EXPECTED_DOMAIN}")
    same_as = data.get("sameAs", [])
    if not isinstance(same_as, list):
        errors.append(f"{source}: sameAs must be a list, got {type(same_as).__name__}")
    else:
        for u in same_as:
            parsed = urlparse(u)
            if not parsed.scheme or not parsed.netloc:
                errors.append(f"{source}: malformed sameAs URL {u!r}")
    return errors


def main():
    site = Path("_site")
    if not site.exists():
        print("ERROR: _site/ doesn't exist. Run `quarto render` first.", file=sys.stderr)
        return 1

    errors = []
    files_with_jsonld = 0
    blocks_validated = 0

    for html_file in sorted(site.rglob("*.html")):
        try:
            html = html_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            errors.append(f"{html_file}: read error ({e})")
            continue
        blocks = JSONLD_RE.findall(html)
        if not blocks:
            continue
        files_with_jsonld += 1
        for block in blocks:
            blocks_validated += 1
            try:
                data = json.loads(block)
            except json.JSONDecodeError as e:
                errors.append(f"{html_file}: invalid JSON-LD ({e})")
                continue
            errors.extend(validate_person(data, str(html_file)))

    if errors:
        print(
            f"Schema validation FAILED ({len(errors)} error(s)):",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"Schema validation OK: {blocks_validated} JSON-LD block(s) "
        f"across {files_with_jsonld} file(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
