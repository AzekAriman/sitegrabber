
import argparse
import asyncio
from sitegrabber.config import Config
from sitegrabber.onepage import grab_one_page

def main():
    ap = argparse.ArgumentParser(description="Grab images from ONE page (no crawling).")
    ap.add_argument("--url", required=True, help="Page URL to collect images from.")
    ap.add_argument("--out", default="./dataset/example", help="Output directory.")
    ap.add_argument("--min-bytes", type=int, default=4000, help="Min file size (bytes).")
    ap.add_argument("--min-wh", nargs=2, type=int, metavar=("MIN_W","MIN_H"), default=[160,160], help="Min WxH.")
    ap.add_argument("--headed", action="store_true", help="Show browser window.")
    ap.add_argument("--captcha", action="store_true", help="Enable captcha handling")
    ap.add_argument("--captcha-wait", type=int, default=25, help="Max seconds to wait for captcha")
    ap.add_argument("--captcha-post-wait", type=float, default=0.0, help="Extra sleep after captcha solved (sec)")

    args = ap.parse_args()

    cfg = Config(
        out_root=args.out,
        min_bytes=args.min_bytes,
        min_w=args.min_wh[0],
        min_h=args.min_wh[1],
        headless=(not args.headed),
        pause_on_captcha=args.captcha,
        captcha_pause_sec=args.captcha_wait,
        captcha_post_wait_sec=args.captcha_post_wait
    )
    asyncio.run(grab_one_page(args.url, args.out, cfg))

if __name__ == "__main__":
    main()
