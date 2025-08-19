
import asyncio
from pathlib import Path
from typing import Set, Tuple
from asyncio import QueueEmpty
from .browser import BrowserCtx
from .config import Config
from .manifest import ManifestWriter
from .extract import extract_image_urls
from .downloader import download_images
from .robots import Robots
from .utils import ensure_dir, is_same_site, domain_folder, norm_join

class SiteCrawler:
    def _drain_queue(self):
        """Очистить очередь to_visit (чтобы не висеть на join())."""
        drained = 0
        while True:
            try:
                self.to_visit.get_nowait()
            except QueueEmpty:
                break
            else:
                self.to_visit.task_done()
                drained += 1
        if drained:
            print(f"[INFO] Drained {drained} queued URLs (page limit reached)")

    def __init__(self, start_url: str, cfg: Config):
        self.start_url = start_url.rstrip("/")
        self.cfg = cfg
        self.domain_dir = Path(cfg.out_root) / domain_folder(self.start_url)
        self.img_dir = self.domain_dir / "images"
        ensure_dir(str(self.img_dir))
        self.manifest = ManifestWriter(str(self.domain_dir / "images_manifest.csv"))

        self.seen_pages: Set[str] = set()
        self.seen_images: Set[str] = set()
        self.to_visit: asyncio.Queue[Tuple[str, int]] = asyncio.Queue()
        self.pages_count = 0
        self.robots = Robots(self.start_url, ua=cfg.user_agent)

    async def close(self):
        self.manifest.close()

    async def run(self):
        async with BrowserCtx(self.cfg.user_agent, self.cfg.headless) as ctx:
            if self.cfg.obey_robots:
                await self.robots.load(ctx)

            # seed
            await self.to_visit.put((self.start_url, 0))

            workers = [asyncio.create_task(self.worker(ctx, i)) for i in range(self.cfg.concurrency)]
            await self.to_visit.join()
            for w in workers:
                w.cancel()

    async def worker(self, ctx, wid: int):
        while True:
            try:
                page_url, depth = await self.to_visit.get()
            except asyncio.CancelledError:
                return
            try:
                await self.process_page(ctx, page_url, depth)
            except Exception as e:
                print(f"[ERR] worker {wid}: {e.__class__.__name__}")
            finally:
                self.to_visit.task_done()
                if self.pages_count >= self.cfg.max_pages:
                    self._drain_queue()
                await asyncio.sleep(self.cfg.throttle_ms / 1000.0)

    async def process_page(self, ctx, page_url: str, depth: int):
        if self.pages_count >= self.cfg.max_pages:
            return
        if page_url in self.seen_pages:
            return
        if self.cfg.obey_robots and not self.robots.allowed(page_url):
            print(f"[ROBOTS] skip {page_url}")
            return
        if not is_same_site(page_url, self.start_url, self.cfg.include_subdomains):
            return

        self.seen_pages.add(page_url)
        self.pages_count += 1
        print(f"[PAGE] {self.pages_count} {page_url} (depth={depth})")
        if self.pages_count >= self.cfg.max_pages:
            self._drain_queue()  # если добавлял ранее метод дренажа очереди

        page = await ctx.new_page()
        try:
            await page.goto(page_url, wait_until="domcontentloaded", timeout=self.cfg.request_timeout_ms)
            # (A) общая пауза на каждой странице
            if self.cfg.pause_on_every_page_sec > 0:
                sec = self.cfg.pause_on_every_page_sec
                print(f"[HUMAN] waiting {sec}s on {page_url} (general pause)")
                for _ in range(sec):
                    await asyncio.sleep(1)

            # (B) пауза, если видим капчу (ждём исчезновения до captcha_pause_sec)
            if self.cfg.pause_on_captcha:
                found = False
                for sel in self.cfg.captcha_selectors:
                    try:
                        if await page.query_selector(sel):
                            found = True
                            break
                    except Exception:
                        pass
                if found:
                    sec = self.cfg.captcha_pause_sec
                    print(f"[HUMAN] captcha detected on {page_url}. Waiting up to {sec}s for you to solve...")
                    for _ in range(sec):
                        # если капча уже исчезла — идём дальше раньше
                        still = False
                        for sel in self.cfg.captcha_selectors:
                            try:
                                if await page.query_selector(sel):
                                    still = True
                                    break
                            except Exception:
                                pass
                        if not still:
                            print("[HUMAN] captcha solved, continue.")
                            if getattr(self.cfg, 'captcha_post_wait_sec', 0) > 0:
                                await asyncio.sleep(self.cfg.captcha_post_wait_sec)
                            break
                        await asyncio.sleep(1)

            # lazy-load
            try:
                for _ in range(self.cfg.scroll_steps):
                    await page.evaluate("() => { window.scrollBy(0, document.body.scrollHeight/2); }")
                    await asyncio.sleep(self.cfg.scroll_pause)
            except Exception:
                pass

            # собрать и скачать картинки
            try:
                urls = await extract_image_urls(page, page_url)
                await download_images(
                    ctx, page_url, urls, str(self.img_dir), self.manifest,
                    self.cfg.min_bytes, self.cfg.min_w, self.cfg.min_h, self.seen_images
                )
            except Exception:
                pass

            # ДОБАВЛЯЕМ НОВЫЕ ССЫЛКИ — ТУТ УЖЕ ЕСТЬ `page`
            if depth < self.cfg.max_depth and self.pages_count < self.cfg.max_pages:
                hrefs = await page.eval_on_selector_all(
                    "a[href]", "els => els.map(e => e.getAttribute('href'))"
                )
                enqueued = 0
                ENQUEUE_LIMIT = 300  # чтобы не раздувать очередь
                for href in hrefs:
                    nu = norm_join(page_url, href)
                    if not nu:
                        continue
                    if is_same_site(nu, self.start_url, self.cfg.include_subdomains) and nu not in self.seen_pages:
                        await self.to_visit.put((nu, depth + 1))
                        enqueued += 1
                        if enqueued >= ENQUEUE_LIMIT:
                            break
        finally:
            await page.close()

    async def run_in_ctx(self, ctx):
        await self.robots.load(ctx)
        await self.to_visit.put((self.start_url, 0))

        workers = [asyncio.create_task(self.worker(ctx, i)) for i in range(self.cfg.concurrency)]
        try:
            # обычное завершение — ждём, пока очередь опустеет
            await self.to_visit.join()
        finally:
            # ВАЖНО: и при нормальном выходе, и при таймауте/отмене
            # сбросить оставшиеся URL — иначе join() мог «держать» воркеров
            self._drain_queue()

            # аккуратно погасить воркеров
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
