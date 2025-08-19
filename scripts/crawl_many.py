import argparse, asyncio
from time import sleep
from sitegrabber.config import Config
from sitegrabber.crawl import SiteCrawler
from sitegrabber.browser import BrowserCtx
from asyncio import wait_for

def load_sites(args):
    sites = []
    if args.start: sites += [s.strip() for s in args.start if s and s.strip()]
    if args.list:
        with open(args.list, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    sites.append(line)
    uniq, seen = [], set()
    for s in sites:
        if s not in seen: seen.add(s); uniq.append(s)
    return uniq

def make_cfg(a):
    return Config(
        out_root=a.out,
        headless=(not a.headed),
        include_subdomains=a.include_subdomains,
        max_pages=a.max_pages,
        max_depth=a.max_depth,
        concurrency=a.concurrency,
        min_bytes=a.min_bytes,
        min_w=a.min_wh[0],
        min_h=a.min_wh[1],
        throttle_ms=a.throttle_ms,
        pause_on_every_page_sec=a.page_wait,
        pause_on_captcha=a.captcha,
        captcha_pause_sec=a.captcha_wait,
        captcha_post_wait_sec=a.captcha_post_wait,
    )



async def main_async(a):
    sites = load_sites(a)
    if not sites: raise SystemExit("No sites provided.")
    cfg = make_cfg(a)
    print(f"[INFO] Sites to crawl: {len(sites)}")
    async with BrowserCtx(cfg.user_agent, cfg.headless) as ctx:
        for i, url in enumerate(sites, 1):
            print(f"\n=== [{i}/{len(sites)}] {url} ===", flush=True)
            crawler = SiteCrawler(url, cfg)
            try:
                await wait_for(crawler.run_in_ctx(ctx), timeout=a.site_timeout)
            finally:
                await crawler.close()
            print(f"[SITE DONE] {url}", flush=True)
            await asyncio.sleep(a.pause_between_sites)

def main():
    ap = argparse.ArgumentParser(description="Crawl MANY sites and download images.")
    ap.add_argument("--start", action="append")
    ap.add_argument("--list")
    ap.add_argument("--out", default="./dataset")
    ap.add_argument("--max-pages", type=int, default=1000)
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--include-subdomains", action="store_true")
    ap.add_argument("--min-bytes", type=int, default=4000)
    ap.add_argument("--min-wh", nargs=2, type=int, metavar=("MIN_W","MIN_H"), default=[160,160])
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--throttle-ms", type=int, default=400)
    ap.add_argument("--pause-between-sites", type=float, default=2.0)
    ap.add_argument("--site-timeout", type=int, default=600, help="Max seconds per site")
    ap.add_argument("--page-wait", type=int, default=0, help="Pause on each page, seconds")
    ap.add_argument("--captcha-wait", type=int, default=25, help="Max seconds to wait for captcha")
    ap.add_argument("--captcha", action="store_true", help="Enable captcha handling")
    ap.add_argument("--captcha-post-wait", type=float, default=0.0, help="Extra sleep after captcha solved (sec)")
    a = ap.parse_args()
    asyncio.run(main_async(a))

if __name__ == "__main__":
    main()
