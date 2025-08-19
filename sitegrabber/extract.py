
from typing import Set
from .utils import norm_join, CSS_BG_URL_PATTERN

META_IMG_SELECTORS = [
    'meta[property="og:image"]',
    'meta[name="og:image"]',
    'meta[property="twitter:image"]',
    'meta[name="twitter:image"]',
]

async def extract_image_urls(page, base_url: str) -> Set[str]:
    """Collect image URLs from <img>, srcset, open graph, twitter, and inline CSS background."""
    urls: Set[str] = set()

    # <img src> + srcset
    try:
        img_srcs = await page.eval_on_selector_all(
            "img",
            """els => els.flatMap(e => {
                const out = [];
                if (e.src) out.push(e.src);
                const ss = e.getAttribute('srcset');
                if (ss) {
                    ss.split(',').forEach(part => {
                        const u = part.trim().split(' ')[0];
                        if (u) out.push(u);
                    });
                }
                return out;
            })"""
        )
        for u in img_srcs:
            nu = norm_join(base_url, u)
            if nu:
                urls.add(nu)
    except Exception:
        pass

    # og:image / twitter:image
    try:
        for sel in META_IMG_SELECTORS:
            metas = await page.eval_on_selector_all(sel, "els => els.map(e => e.getAttribute('content'))")
            for u in metas:
                nu = norm_join(base_url, u)
                if nu:
                    urls.add(nu)
    except Exception:
        pass

    # CSS inline background-image
    try:
        styles = await page.eval_on_selector_all("*[style]", "els => els.map(e => e.getAttribute('style'))")
        for st in styles:
            for m in CSS_BG_URL_PATTERN.findall(st or ""):
                nu = norm_join(base_url, m)
                if nu:
                    urls.add(nu)
    except Exception:
        pass

    # link rel preload/image
    try:
        link_imgs = await page.eval_on_selector_all(
            'link[as="image"], link[rel="preload"][as="image"], link[rel="image_src"]',
            "els => els.map(e => e.getAttribute('href'))"
        )
        for u in link_imgs:
            nu = norm_join(base_url, u)
            if nu:
                urls.add(nu)
    except Exception:
        pass

    return urls
