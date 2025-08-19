
from dataclasses import dataclass

@dataclass
class Config:
    out_root: str = "./dataset"
    user_agent: str = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/122.0.0.0 Safari/537.36")
    headless: bool = True

    # filters
    min_bytes: int = 4000
    min_w: int = 160
    min_h: int = 160

    # network/browser
    request_timeout_ms: int = 90000
    scroll_steps: int = 6
    scroll_pause: float = 0.8

    # crawl
    include_subdomains: bool = False
    throttle_ms: int = 200
    max_pages: int = 1000
    max_depth: int = 4
    concurrency: int = 5
    # --- человеческий режим ---
    pause_on_every_page_sec: int = 0  # общая пауза после загрузки страницы
    pause_on_captcha: bool = False  # ждать, если видим капчу
    captcha_pause_sec: int = 25  # сколько секунд ждать капчу
    captcha_post_wait_sec: float = 0.0  # пауза после решения капчи (сек), 0 — без паузы
    captcha_selectors: tuple[str, ...] = (
        "iframe[title*='captcha']",
        "div.g-recaptcha", "div.h-captcha",
        "input[name='cf-turnstile-response']",
        "#cf-challenge-running", "#challenge-form",
        "div.cf-challenge", "div#cf-stage"
    )
    request_timeout_ms: int = 90000  # чтобы страница не отваливалась, пока кликаешь
