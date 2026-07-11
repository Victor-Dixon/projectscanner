"""Static website link inventory — repo-local nav/href triage for websites repos."""

from __future__ import annotations

import json
import re
import urllib.parse
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

SCHEMA = "projectscanner.website_link_inventory.v1"

SKIP_HREF_PREFIXES = ("mailto:", "tel:", "javascript:", "#", "data:")
SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "vendor",
    "wp-includes",
    "wp-admin",
}
ASSET_SUFFIXES = {
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".json",
    ".pdf",
    ".map",
}

SITE_ROOT_GLOBS = (
    "sites/production/websites/*",
    "websites/*",
    "runtime/content/*",
    "runtime/content/parked_domains/*",
    "routes/*",
)


@dataclass
class LinkRow:
    domain: str
    source_file: str
    href: str
    normalized_path: str
    link_kind: str
    local_exists: bool
    resolved_file: str = ""
    notes: str = ""


@dataclass
class SiteInventory:
    domain: str
    ssot_root: str
    html_files: int = 0
    nav_links: list[LinkRow] = field(default_factory=list)
    internal_links: list[LinkRow] = field(default_factory=list)
    broken_local: list[LinkRow] = field(default_factory=list)
    orphan_pages: list[str] = field(default_factory=list)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def normalize_path(path: str) -> str:
    path = urllib.parse.unquote(path or "/").strip()
    if not path.startswith("/"):
        path = "/" + path
    path = re.sub(r"/+", "/", path)
    if path != "/" and path.endswith("/"):
        return path
    if path != "/" and not path.endswith("/") and "." not in Path(path).name:
        return path + "/"
    return path or "/"


def discover_site_roots(repo_root: Path) -> dict[str, Path]:
    """Map domain -> best SSOT root (production_sync wins over legacy)."""
    priority = {
        "sites/production/websites": 100,
        "runtime/content/parked_domains": 85,
        "runtime/content": 80,
        "routes": 70,
        "websites": 60,
    }
    skip_names = {"parked_domains", "shared", "templates", "overlays", "weareswarm"}
    found: dict[str, tuple[int, Path]] = {}
    for pattern in SITE_ROOT_GLOBS:
        prefix = pattern.rsplit("/*", 1)[0]
        rank = priority.get(prefix, 0)
        for child in sorted(repo_root.glob(pattern)):
            if not child.is_dir():
                continue
            domain = child.name
            if domain in skip_names:
                continue
            prev = found.get(domain)
            if prev is None or rank > prev[0]:
                found[domain] = (rank, child)
    return {domain: path for domain, (_, path) in found.items()}


def fallback_roots(repo_root: Path, domain: str, primary: Path) -> list[Path]:
    """Lower-priority trees for the same domain — used to resolve cross-tree href targets."""
    candidates = [
        repo_root / "runtime/content" / domain,
        repo_root / "websites" / domain,
        repo_root / "routes" / domain,
        repo_root / "runtime/content/parked_domains" / domain,
    ]
    out: list[Path] = []
    for path in candidates:
        if path.is_dir() and path.resolve() != primary.resolve():
            out.append(path)
    return out


def iter_html_files(site_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in site_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() in {".html", ".htm", ".php"}:
            files.append(path)
    return files


def build_path_index(site_root: Path) -> dict[str, Path]:
    """Map normalized URL paths to repo files under site root."""
    index: dict[str, Path] = {}
    for path in site_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        rel = path.relative_to(site_root).as_posix()
        if path.name == "index.html":
            parent = path.parent.relative_to(site_root).as_posix()
            url_path = "/" if parent == "." else normalize_path(f"/{parent}/")
            index[url_path] = path
        if path.suffix.lower() in {".html", ".htm"}:
            index[normalize_path(f"/{rel}")] = path
            stem = path.stem
            parent = path.parent.relative_to(site_root).as_posix()
            if parent == ".":
                index[normalize_path(f"/{stem}/")] = path
                index[normalize_path(f"/{stem}.html")] = path
            else:
                index[normalize_path(f"/{parent}/{stem}/")] = path
                index[normalize_path(f"/{parent}/{stem}.html")] = path
    if (site_root / "index.html").is_file():
        index["/"] = site_root / "index.html"
    return index


def extract_hrefs(html: str) -> list[tuple[str, str]]:
    """Return (href, link_kind) pairs from HTML."""
    rows: list[tuple[str, str]] = []
    nav_blocks = re.findall(r"<nav[^>]*>(.*?)</nav>", html, flags=re.I | re.S)
    for block in nav_blocks:
        for href in re.findall(r"""href\s*=\s*['"]([^'"]+)['"]""", block, flags=re.I):
            rows.append((href.strip(), "nav"))
    for href in re.findall(r"""href\s*=\s*['"]([^'"]+)['"]""", html, flags=re.I):
        href = href.strip()
        if not href or any(href.lower().startswith(p) for p in SKIP_HREF_PREFIXES):
            continue
        if not any(href == n for n, _ in rows):
            rows.append((href, "inline"))
    return rows


def resolve_local(
    path_index: dict[str, Path],
    href: str,
    domain: str,
    source_file: Path | None = None,
    site_root: Path | None = None,
) -> tuple[str, bool, Path | None, str]:
    if "<?" in href or "?>" in href or href.startswith("<?"):
        return href, True, None, "php_template"
    parsed = urllib.parse.urlparse(href)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return href, True, None, "external_scheme"
    if parsed.netloc:
        host = parsed.netloc.lower().removeprefix("www.")
        if host and host != domain.lower().removeprefix("www."):
            return normalize_path(parsed.path or "/"), True, None, "external_domain"
    raw_path = parsed.path or "/"
    if not parsed.netloc and source_file and site_root and not raw_path.startswith("/"):
        # Resolve ./page.html and ../sibling/ relative to source HTML file.
        base_dir = source_file.parent
        target = (base_dir / raw_path.split("#", 1)[0].split("?", 1)[0]).resolve()
        try:
            rel = target.relative_to(site_root.resolve())
            raw_path = "/" + rel.as_posix()
        except ValueError:
            return normalize_path("/" + raw_path), False, None, "missing_local_target"
    norm = normalize_path(raw_path.split("#", 1)[0].split("?", 1)[0])
    if norm.endswith(tuple(ASSET_SUFFIXES)):
        return norm, True, None, "asset"
    candidates = [norm]
    if not norm.endswith("/"):
        candidates.append(norm + "/")
    if norm.endswith("/"):
        candidates.append(norm.rstrip("/") + ".html")
    for cand in candidates:
        if cand in path_index and path_index[cand].is_file():
            return norm, True, path_index[cand], ""
    return norm, False, None, "missing_local_target"


def scan_site(domain: str, site_root: Path, repo_root: Path) -> SiteInventory:
    inv = SiteInventory(domain=domain, ssot_root=str(site_root.relative_to(repo_root)).replace("\\", "/"))
    path_index = build_path_index(site_root)
    for extra in fallback_roots(repo_root, domain, site_root):
        for key, val in build_path_index(extra).items():
            if val.is_file() and key not in path_index:
                path_index[key] = val
    html_files = iter_html_files(site_root)
    inv.html_files = len(html_files)

    seen_nav: set[tuple[str, str]] = set()
    linked_paths: set[str] = set()
    all_rows: list[LinkRow] = []

    for html_path in html_files:
        rel_source = html_path.relative_to(repo_root).as_posix()
        try:
            text = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for href, kind in extract_hrefs(text):
            norm, exists, resolved, note = resolve_local(
                path_index, href, domain, source_file=html_path, site_root=site_root
            )
            linked_paths.add(norm)
            row = LinkRow(
                domain=domain,
                source_file=rel_source,
                href=href,
                normalized_path=norm,
                link_kind=kind,
                local_exists=exists,
                resolved_file=resolved.relative_to(repo_root).as_posix() if resolved else "",
                notes=note,
            )
            all_rows.append(row)
            key = (href, rel_source)
            if kind == "nav" and key not in seen_nav:
                seen_nav.add(key)
                inv.nav_links.append(row)
            if kind == "inline":
                inv.internal_links.append(row)
            if not exists and note == "missing_local_target":
                inv.broken_local.append(row)

    for url_path, file_path in path_index.items():
        if file_path.suffix.lower() not in {".html", ".htm"}:
            continue
        if url_path not in linked_paths and url_path not in {"/"}:
            inv.orphan_pages.append(url_path)

    return inv


def build_inventory(repo_root: Path, domain_filter: str | None = None) -> dict:
    repo_root = repo_root.resolve()
    sites = discover_site_roots(repo_root)
    if domain_filter:
        sites = {k: v for k, v in sites.items() if k == domain_filter}

    site_rows: dict[str, dict] = {}
    total_nav = 0
    total_broken = 0
    total_orphans = 0

    for domain, site_root in sorted(sites.items()):
        inv = scan_site(domain, site_root, repo_root)
        total_nav += len(inv.nav_links)
        total_broken += len({(r.normalized_path, r.href) for r in inv.broken_local})
        total_orphans += len(inv.orphan_pages)
        site_rows[domain] = {
            "ssot_root": inv.ssot_root,
            "html_files": inv.html_files,
            "nav_links": [asdict(r) for r in inv.nav_links],
            "broken_local": [asdict(r) for r in inv.broken_local],
            "orphan_pages": inv.orphan_pages,
            "internal_link_count": len(inv.internal_links),
        }

    return {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "repo_root": str(repo_root),
        "summary": {
            "sites_scanned": len(site_rows),
            "nav_links": total_nav,
            "broken_local_unique": total_broken,
            "orphan_pages": total_orphans,
        },
        "sites": site_rows,
        "verify_cmd": "python scripts/intelligence/emit_website_link_inventory.py <repo>",
    }


def write_inventory(repo_root: Path, output_path: Path | None = None, domain_filter: str | None = None) -> Path:
    doc = build_inventory(repo_root, domain_filter=domain_filter)
    if output_path is None:
        output_path = repo_root / "runtime" / "state" / "website_link_inventory_latest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return output_path
