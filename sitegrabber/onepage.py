
import asyncio
from pathlib import Path

from .browser import BrowserCtx
from .config import Config
from .manifest import ManifestWriter
from .extract import extract_image_urls
from .downloader import download_images
from .utils import ensure_dir

async def grab_one_page(url: str, out_dir: str, cfg: Config):
    ensure_dir(out_dir)
    img_dir = str(Path(out_dir) / "images")
    ensure_dir(img_dir)
    manifest = ManifestWriter(str(Path(out_dir) / "images_manifest.csv"))

    async with BrowserCtx(cfg.user_agent, cfg.headless) as ctx:
        page = await ctx.new_page()
        print(f"[INFO] Open {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=cfg.request_timeout_ms)

        # trigger lazy-load
        for _ in range(cfg.scroll_steps):
            await page.evaluate("() => { window.scrollBy(0, document.body.scrollHeight/2); }")
            await asyncio.sleep(cfg.scroll_pause)

        urls = await extract_image_urls(page, url)
        print(f"[INFO] candidates: {len(urls)}")

        seen = set()
        ok, skipped = await download_images(
            ctx=ctx,
            page_url=url,
            urls=urls,
            img_dir=img_dir,
            manifest=manifest,
            min_bytes=cfg.min_bytes,
            min_w=cfg.min_w,
            min_h=cfg.min_h,
            seen=seen,
        )

        await page.close()
    manifest.close()
    print(f"[DONE] saved={ok} skipped={skipped} manifest={Path(out_dir)/'images_manifest.csv'}")
