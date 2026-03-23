#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
CONTENT_DIR = ROOT / "content"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
SITE_DIR = ROOT / "site"
PAGES_FILE = ROOT / "pages.json"

PLACEHOLDERS = (
    "title",
    "description",
    "header_title",
    "header_subtitle",
    "preload",
    "nav",
    "content",
    "footer",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def load_pages() -> dict[str, dict]:
    return json.loads(read_text(PAGES_FILE))


def render_links(items: list[list[str]]) -> str:
    links: list[str] = []

    for item in items:
        if len(item) == 2:
            href, label = item
            attrs = ""
        elif len(item) == 3:
            href, label, extra_attr = item
            attrs = f" {extra_attr}" if extra_attr else ""
        else:
            raise ValueError(f"bad link entry: {item!r}")

        links.append(f'<a href="{href}"{attrs}>{label}</a>')

    return " |\n        ".join(links)


def render_template(template: str, values: dict[str, str]) -> str:
    rendered = template

    for key in PLACEHOLDERS:
        rendered = rendered.replace(f"{{{{ {key} }}}}", values.get(key, ""))

    return rendered


def clean_site_dir() -> None:
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True, exist_ok=True)


def copy_assets() -> None:
    if not ASSETS_DIR.exists():
        return

    shutil.copytree(ASSETS_DIR, SITE_DIR / "assets", dirs_exist_ok=True)


def build_pages() -> None:
    template = read_text(TEMPLATES_DIR / "base.html")
    pages = load_pages()

    for output_name, page in pages.items():
        content_path = ROOT / page["content_file"]

        values = {
            "title": page["title"],
            "description": page.get("description", ""),
            "header_title": page.get("header_title", ""),
            "header_subtitle": page.get("header_subtitle", ""),
            "preload": page.get("preload", ""),
            "nav": render_links(page.get("nav", [])),
            "content": read_text(content_path),
            "footer": render_links(page.get("footer", [])),
        }

        html = render_template(template, values)
        write_text(SITE_DIR / output_name, html)
        print(f"built {output_name}")


def main() -> None:
    clean_site_dir()
    copy_assets()
    build_pages()
    print("done")


if __name__ == "__main__":
    main()
