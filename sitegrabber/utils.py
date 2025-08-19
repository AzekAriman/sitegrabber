
import hashlib
import os
import re
from urllib.parse import urljoin, urlparse, urlunparse

import tldextract

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".avif"}
ALLOWED_CT = {
    "image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp", "image/avif"
}
CSS_BG_URL_PATTERN = re.compile(r'url\(["\']?(.*?)["\']?\)', re.IGNORECASE)

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "ignore")).hexdigest()

def guess_ext(content_type: str, url: str) -> str:
    mapper = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/bmp": ".bmp",
    }
    if content_type in mapper:
        return mapper[content_type]
    path = urlparse(url).path.lower()
    for ext in IMG_EXTS:
        if path.endswith(ext):
            return ext
    return ".jpg"

def norm_join(base: str, href: str) -> str | None:
    if not href:
        return None
    href = href.strip()
    if href.startswith(("data:", "blob:")):
        return None
    try:
        u = urljoin(base, href)
        p = urlparse(u)
        if not p.scheme.startswith("http"):
            return None
        # drop fragment
        u = urlunparse(p._replace(fragment=""))
        return u
    except Exception:
        return None

def is_same_site(target: str, root: str, include_subdomains: bool) -> bool:
    t = tldextract.extract(target)
    r = tldextract.extract(root)
    if (t.domain, t.suffix) != (r.domain, r.suffix):
        return False
    if include_subdomains:
        return True
    return (t.subdomain or "") == (r.subdomain or "")

def domain_folder(url: str) -> str:
    p = urlparse(url)
    return p.netloc.replace(":", "_")
