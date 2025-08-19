
import argparse
import asyncio
from sitegrabber.config import Config
from sitegrabber.crawl import SiteCrawler

def main():
    ap = argparse.ArgumentParser(description="Crawl a whole site and download images from internal pages.")
    ap.add_argument("--start", required=True, help="Start URL (site root).")
    ap.add_argument("--out", default="./dataset", help="Output root directory.")
    ap.add_argument("--max-pages", type=int, default=1000)
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--concurrency", type=int, default=5)
    ap.add_argument("--include-subdomains", action="store_true")
    ap.add_argument("--min-bytes", type=int, default=4000)
    ap.add_argument("--min-wh", nargs=2, type=int, metavar=("MIN_W","MIN_H"), default=[160,160])
    ap.add_argument("--captcha", action="store_true")
    ap.add_argument("--captcha-wait", type=int, default=25)
    ap.add_argument("--captcha-post-wait", type=float, default=0.0)

    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--throttle-ms", type=int, default=200)
    args = ap.parse_args()

    cfg = Config(
        out_root=args.out,
        headless=(not args.headed),
        include_subdomains=args.include_subdomains,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        concurrency=args.concurrency,
        min_bytes=args.min_bytes,
        min_w=args.min_wh[0],
        min_h=args.min_wh[1],
        throttle_ms=args.throttle_ms,
        pause_on_captcha=args.captcha,
        captcha_pause_sec=args.captcha_wait,
        captcha_post_wait_sec=args.captcha_post_wait,
    )
    crawler = SiteCrawler(args.start, cfg)
    try:
        asyncio.run(crawler.run())
    finally:
        asyncio.run(crawler.close())

if __name__ == "__main__":
    main()
