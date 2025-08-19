# SiteGrabber — README (RU)

Этот документ — краткое и понятное руководство к запуску нашего сборщика изображений.

## 0) Установка 

```powershell
python -m venv venv
# Windows
.\venv\Scripts\activate

python -m pip install --upgrade pip wheel
python -m pip install -r requirements.txt
python -m playwright install chromium
```

> Все команды ниже запускаются **из корня проекта** (где лежат папки `sitegrabber/` и `scripts/`).

---

## 1) Режим «один сайт» 

Пример на домене `winestate.ru` (замени на свой):

```powershell
python -m scripts.crawl_site --start https://winestate.ru/ --out .\dataset --max-pages 8000 --max-depth 6 --concurrency 1 --include-subdomains --headed --throttle-ms 1200 --min-bytes 10000 --min-wh 180 180
```

**Что делают параметры:**

* `--start` — стартовый URL домена.
* `--out` — корень вывода (для домена создастся `./dataset/<домен>/`).
* `--max-pages` — бюджет страниц на сайт (сколько URL максимум открыть).
* `--max-depth` — глубина переходов по ссылкам (насколько «вглубь» идём).
* `--concurrency 1` — одна вкладка (удобно проходить капчи вручную).
* `--include-subdomains` — захватывать поддомены (`cdn.`, `img.` и т.п.).
* `--headed` — видимое окно браузера.
* `--throttle-ms` — «вежливая» пауза между страницами (в миллисекундах).
* `--min-bytes`, `--min-wh` — фильтры: отсекаем мелкие превью.

---

## 2) Режим «много сайтов списком» (sites.txt)

Создай `sites.txt` c одним URL в строке и запускай `crawl_many`:

### 2.1 Без капчи

```powershell
python -m scripts.crawl_many --list .\sites.txt --out .\dataset --max-pages 300 --max-depth 6 --concurrency 1 --include-subdomains --headed --throttle-ms 1200 --pause-between-sites 10 --site-timeout 900 --min-bytes 10000 --min-wh 180 180
```

**Добавочные параметры:**

* `--list` — файл со списком доменов.
* `--pause-between-sites` — пауза между сайтами (сек.), чтобы быть «вежливее» и успевать смотреть на окно.
* `--site-timeout` — предохранитель: максимум секунд на один сайт (если «залип», идём дальше).

### 2.2 С капчей (ручной проход)

```powershell
python -m scripts.crawl_many --list .\sites.txt --out .\dataset --max-pages 300 --max-depth 6 --concurrency 1 --include-subdomains --headed --throttle-ms 1200 --pause-between-sites 10 --site-timeout 900 --page-wait 5 --captcha --captcha-wait 90 --captcha-post-wait 20 --min-bytes 10000 --min-wh 180 180
```

**Что добавили для капчи:**

* `--captcha` — включить «человеческий режим» (скрипт смотрит признаки капчи и ждёт).
* `--captcha-wait` — сколько ждать (сек.) пока ты пройдёшь капчу на странице.
* `--captcha-post-wait` — дополнительная короткая пауза после прохождения капчи (сек.), чтобы страница успела прогрузиться.
* `--page-wait` — небольшая пауза на **каждой** странице (сек.) — полезно для агрессивных сайтов.

> Примечание: если капча встречается только на определённой глубине (например, `depth=1`), в конфиге можно указать, **на каких глубинах** ждать капчу (поле `captcha_depths`). Тогда ожидание будет только там, где нужно.

---

## 3) Где лежат результаты

Структура для каждого домена:

```
./dataset/
  <домен>/
    images/               # скачанные картинки (имена — SHA1 от URL + расширение)
    images_manifest.csv   # журнал загрузок
```

### `images_manifest.csv` — колонки

* `timestamp` — время записи (unix).
* `page_url` — страница, с которой собрана ссылка на картинку.
* `image_url` — прямой URL картинки.
* `local_path` — куда сохранён файл локально.
* `content_type` — тип данных (image/jpeg/png/webp/...)
* `size_bytes` — размер файла.
* `width`, `height` — ширина/высота (если удалось определить).
* `status` — итог по объекту:

  * `ok` — успешно сохранено;
  * `skip_content_type` / `skip_too_small` / `skip_small_wh` — отфильтровано (тип/байты/размеры);
  * `http XXX` — код ответа сервера (403/404/429 и т.п.);
  * `err:...` — техническая ошибка при скачивании/декодировании.

---

## 4) Практические советы

* **Глубокий сбор**: поднимай `--max-pages` и `--max-depth`. Стартуй из разделов каталога, а не с главной.
* **Вежливость и блокировки**: держи `--concurrency 1–3`, `--throttle-ms 800–1500`, `--pause-between-sites 5–15`.
* **CDN**: включай `--include-subdomains`, иначе картинки с `cdn.`/`img.` могут не попасть.
* **Фильтры качества**: повышай `--min-bytes` и `--min-wh`, чтобы не тянуть мелкие превью.
* **Robots.txt**: в логе `[ROBOTS] skip ...` — это нормально, обходим запретные пути на сайте.
* **Очередь ссылок**: сообщение вида `[INFO] Drained N queued URLs (page limit reached)` означает, что достигнут лимит `--max-pages`, остаток очереди очищен и сайт завершён.

---

## 5) Быстрые пресеты

**Быстрый тест:**

```powershell
python -m scripts.crawl_site --start https://example.com/ --out .\dataset --max-pages 30 --max-depth 3 --concurrency 1 --include-subdomains --headed --throttle-ms 1200
```

**Глубокий сбор одного сайта:**

```powershell
python -m scripts.crawl_site --start https://example.com/ --out .\dataset --max-pages 5000 --max-depth 6 --concurrency 1 --include-subdomains --headed --throttle-ms 1200 --min-bytes 12000 --min-wh 180 180
```

**Много сайтов без капчи:**

```powershell
python -m scripts.crawl_many --list .\sites.txt --out .\dataset --max-pages 300 --max-depth 6 --concurrency 1 --include-subdomains --headed --throttle-ms 1200 --pause-between-sites 10 --site-timeout 900 --min-bytes 10000 --min-wh 180 180
```

**Много сайтов c капчей:**

```powershell
python -m scripts.crawl_many --list .\sites.txt --out .\dataset --max-pages 300 --max-depth 6 --concurrency 1 --include-subdomains --headed --throttle-ms 1200 --pause-between-sites 10 --site-timeout 900 --page-wait 5 --captcha --captcha-wait 90 --captcha-post-wait 20 --min-bytes 10000 --min-wh 180 180
```

---

## 6) Возможные проблемы 

* **`ModuleNotFoundError: playwright`** — поставь зависимости в тот Python, где запускаешь:

  ```powershell
  python -m pip install -r requirements.txt
  python -m playwright install chromium
  ```
* **Окно закрылось после сайта** — проверь, что используешь `crawl_many` с одним окном на все сайты и видишь в логе `[SITE DONE] ...` (актуальная версия скрипта).
* **Всё «встало»** — включи таймаут на сайт `--site-timeout`, ограничь число ссылок, добавляемых с одной страницы (ENQUEUE\_LIMIT), и проверь, что `throttle_ms` — число (а не объект `Namespace`).
* **Не успеваешь на капчу** — `--headed`, `--concurrency 1`, `--captcha-wait` увеличить, можно добавить `--page-wait`.

---

## 7) Что ещё хотелось бы сделать

* **Авто‑проход капч/антибот‑проверок.** Это частично возможно, но не гарантируется и зависит от правил конкретных сайтов. Возможно стоит изучить внешние сервисы распознавания (например, 2captcha / anti‑captcha / hCaptcha-сервисы), но обход Cloudflare/Turnstile часто невозможен без нарушений.

* **Постоянный профиль браузера.** Добавить режим persistent context (хранение профиля/куки), чтобы решённая капча на домене сохранялась и действовала на следующих страницах.
