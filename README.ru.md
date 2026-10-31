# NoDpiTube

<div align="center">
  <img src="assets/app_icon_xxxhdpi.png" width="128" height="128" alt="YouTube Icon" />
  <h1>NoDpiTube</h1>
  <p><b>Ультимативный клиент YouTube для Android TV со встроенным обходом DPI-блокировок</b></p>
  <p><i>Объединение <a href="https://github.com/yuliskov/SmartTube">SmartTube</a> и ядра <a href="https://github.com/GVCoder09/NoDPI4Android">NoDPI</a></i></p>
</div>

---

## 🚀 Основные возможности

* 🛡️ **Встроенный обход блокировок (NoDPI):**  
  Трафик YouTube фрагментируется на уровне TLS ClientHello (разбиение SNI на чанки + отправка первого чанка с `TTL = 1` для disorder-эффекта). Не требует root-прав, не занимает единственный VPN-слот в Android и не требует настройки прокси в Wi-Fi телевизора.
* ⚡ **Сетевой стек Chromium (Cronet) по умолчанию:**  
  Плеер изначально сконфигурирован на работу через встроенный Chromium Cronet с принудительно отключенным QUIC (HTTP/3), благодаря чему все видеопотоки и API стабильно проходят сквозь фильтры ТСПУ/DPI без зависаний.
* 📺 **Оригинальный интерфейс и брендинг:**  
  Приложение называется **YouTube**, использует классическую красную иконку и фирменный 16:9 Leanback-баннер для домашнего экрана Android TV / Google TV.
* 👯 **Установка «Рядом» (Параллельная установка):**  
  Изменен `applicationId` (`com.teamsmart.videomanager.tv.nodpi`). Приложение не конфликтует и устанавливается рядом с оригинальным SmartTube или официальным клиентом YouTube.
* 🔄 **Автоматическая пересборка через GitHub Actions:**  
  Специальный воркфлоу раз в 12 часов проверяет появление новых релизов в официальном репозитории `yuliskov/SmartTube` и коммитов в `NoDPI`. Как только выходит обновление, GitHub Actions автоматически собирает свежий APK и выкладывает его в Releases.
* 📲 **Встроенное автообновление прямо на ТВ:**  
  Приложение само проверяет манифест обновлений в ваших GitHub Releases (`update.json`). Когда выйдет новая версия, на экране ТВ появится уведомление с предложением обновиться в один клик с пульта.

---

## 🛠️ Как запустить свой репозиторий NoDpiTube

Вам **не нужно** устанавливать Android Studio или SDK на свой компьютер. Вся компиляция происходит бесплатно на серверах GitHub Actions.

### Шаг 1. Создание репозитория на GitHub
1. Перейдите на [GitHub New Repository](https://github.com/new).
2. Назовите репозиторий **`NoDpiTube`** (публичный или приватный).
3. Загрузите файлы этого проекта в свой новый репозиторий:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of NoDpiTube"
   git branch -M main
   git remote add origin https://github.com/commensal/NoDpiTube.git
   git push -u origin main
   ```

### Шаг 2. Настройка прав для GitHub Actions
Чтобы GitHub Actions мог публиковать релизы с файлами APK и запускать фоновые задачи:
1. В вашем репозитории перейдите в **Settings** → **Actions** → **General**.
2. Прокрутите вниз до раздела **Workflow permissions**.
3. Выберите пункт **Read and write permissions** (Разрешить чтение и запись).
4. Поставьте галочку **Allow GitHub Actions to create and approve pull requests**.
5. Нажмите **Save**.

### Шаг 3. Первый запуск сборки
1. Откройте вкладку **Actions** в репозитории.
2. В левой колонке выберите воркфлоу **Build NoDpiTube**.
3. Нажмите кнопку **Run workflow** справа.
4. Сборка займет 5–8 минут.
5. После завершения перейдите на страницу репозитория в раздел **Releases** — там будут готовы файлы `.apk` и `update.json`.

---

## 📥 Какой APK устанавливать на устройство?

* **`NoDpiTube-v...-universal.apk`** — универсальная сборка (рекомендуется). Подходит для любых телевизоров, приставок и медиаплееров.
* **`NoDpiTube-v...-arm64-v8a.apk`** — для современных приставок с 64-битным процессором (Nvidia Shield, современные Google TV / Ugoos).
* **`NoDpiTube-v...-armeabi-v7a.apk`** — для большинства бюджетных ТВ, приставок и стиков (Xiaomi Mi Box / Stick, Realme и т.д.).

---

## ⚙️ Структура проекта

```
NoDpiTube/
├── .github/
│   └── workflows/
│       ├── build.yml             # Главный воркфлоу сборки и создания релизов
│       └── check_upstream.yml    # Мониторинг обновлений SmartTube и NoDPI раз в 12 часов
├── src/
│   └── nodpi/                    # Ядро NoDPI на чистом Kotlin
│       ├── TlsFragmenter.kt      # Фрагментация ClientHello и разделение SNI
│       ├── Disorder.kt           # Манипуляция с TTL=1 (out-of-order для обхода DPI)
│       ├── CloudflareRanges.kt   # Исключение Cloudflare CDN во избежание зависаний
│       ├── Blacklist.kt          # Списки доменов YouTube и Google Video CDN
│       ├── ProxyConfig.kt        # Конфигурация локального прокси
│       ├── ProxyServer.kt        # Встроенный HTTP/HTTPS CONNECT прокси-сервер
│       └── NoDpiManager.kt       # Менеджер автозапуска и системных настроек
├── assets/
│   ├── generate_pngs.py          # Генератор иконок YouTube и баннеров для ТВ
│   └── generate_assets.py        # Pillow-генератор ассетов
├── scripts/
│   ├── apply_patches.py          # Мастер-скрипт внедрения NoDPI и настроек в SmartTube
│   └── generate_update_json.py   # Генератор манифеста update.json для встроенного обновления
├── build_local.py                # Скрипт для сборки на локальном компьютере
├── README.md
└── README.ru.md
```

---

## 📜 Лицензия
Проект распространяется по лицензии GPL v3 в соответствии с лицензиями исходных проектов [SmartTube](https://github.com/yuliskov/SmartTube) и [NoDPI4Android](https://github.com/GVCoder09/NoDPI4Android).
