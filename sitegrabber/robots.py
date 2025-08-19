
from urllib.parse import urljoin, urlparse
from urllib import robotparser

class Robots:
    def __init__(self, root_url: str, ua: str = "*"):
        p = urlparse(root_url)
        self.base = f"{p.scheme}://{p.netloc}"
        self.ua = ua
        self.rp = robotparser.RobotFileParser()
        self.loaded = False

    async def load(self, ctx):
        try:
            robots_url = urljoin(self.base, "/robots.txt")
            resp = await ctx.request.get(robots_url)
            if resp.ok:
                txt = await resp.text()
                self.rp.parse(txt.splitlines())
                self.loaded = True
        except Exception:
            self.loaded = False

    def allowed(self, url: str) -> bool:
        if not self.loaded:
            return True
        try:
            return self.rp.can_fetch(self.ua, url)
        except Exception:
            return True
