
# sitegrabber (modular)

Два сценария:

1. **Одна страница** (быстрый тест и отладка путей/фильтров):
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   playwright install chromium

   python scripts/grab_one_page.py \
     --url https://example.com/catalog \
     --out ./dataset/example \
     --headed
   ```

2. **Весь сайт** (с обходом внутренних ссылок, уважением robots.txt):
   ```bash
   python scripts/crawl_site.py \
     --start https://example.com \
     --out ./dataset \
     --max-pages 1500 \
     --max-depth 4 \
     --concurrency 4 \
     --include-subdomains \
     --headed
   ```

### Где лежит результат

- Картинки: `./dataset/<domain>/images/...`
- Манифест: `./dataset/<domain>/images_manifest.csv` (для одной страницы — выбирайте свой `--out`)

Колонки манифеста:
`timestamp,page_url,image_url,local_path,content_type,size_bytes,width,height,status`

### Настройки фильтров

- `--min-bytes` отсекает маленькие превью
- `--min-wh` задаёт порог по ширине/высоте (если удаётся прочитать через Pillow)

### Небольшие подсказки

- Если ловите бан (429/403), снизьте `--concurrency`, включите `--headed`, увеличьте задержку `--throttle-ms`.
- Для сайтов, где картинки на CDN-сабдоменах (`cdn.`, `img.`), используйте `--include-subdomains`.
- Хотите собрать именно Alcohol/Weapon — запускайте краулер от разделов каталога, а не от главной.
