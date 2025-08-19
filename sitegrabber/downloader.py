
from io import BytesIO
from typing import Iterable, Set

from PIL import Image

from .manifest import ManifestWriter
from .utils import ALLOWED_CT, guess_ext, sha1
from pathlib import Path

async def download_images(ctx, page_url: str, urls: Iterable[str], img_dir: str,
                          manifest: ManifestWriter, min_bytes: int, min_w: int, min_h: int,
                          seen: Set[str]):
    ok, skipped = 0, 0
    for iu in urls:
        if iu in seen:
            continue
        seen.add(iu)
        try:
            resp = await ctx.request.get(iu, timeout=45000)
            if not resp.ok:
                manifest.write(page_url, iu, "", "", 0, 0, 0, f"http {resp.status}")
                continue

            body = await resp.body()
            ct = resp.headers.get("content-type", "").split(";")[0].strip().lower()
            size = len(body)

            if ct and ct not in ALLOWED_CT:
                manifest.write(page_url, iu, "", ct, size, 0, 0, "skip_content_type")
                skipped += 1
                continue
            if size < min_bytes:
                manifest.write(page_url, iu, "", ct, size, 0, 0, "skip_too_small")
                skipped += 1
                continue

            width = height = 0
            try:
                im = Image.open(BytesIO(body))
                width, height = im.size
            except Exception:
                pass

            if (width and width < min_w) or (height and height < min_h):
                manifest.write(page_url, iu, "", ct, size, width, height, "skip_small_wh")
                skipped += 1
                continue

            ext = guess_ext(ct, iu)
            fname = f"{sha1(iu)}{ext}"
            fpath = (Path(img_dir) / fname)
            fpath.write_bytes(body)

            manifest.write(page_url, iu, str(fpath), ct, size, width, height, "ok")
            ok += 1
            if (ok + skipped) % 20 == 0:
                print(f"[DL] {ok} ok / {skipped} skip on {page_url}")
        except Exception as e:
            manifest.write(page_url, iu, "", "", 0, 0, 0, f"err:{type(e).__name__}")
    print(f"[DL] done page={page_url}: {ok} ok, {skipped} skip")
    return ok, skipped
