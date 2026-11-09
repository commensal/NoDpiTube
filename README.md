# NoDpiTube (YouTube для Android TV)

<div align="center">
  <img src="assets/app_icon_xxxhdpi.png" width="128" height="128" alt="YouTube Icon" />
  <h1>NoDpiTube</h1>
  <p><b>Клиент YouTube для Android TV со встроенным обходом DPI</b></p>
  <p><i>Плеер <a href="https://github.com/yuliskov/SmartTube">SmartTube</a>, метод обхода из <a href="https://github.com/theo0x0/nodpi">nodpi</a></i></p>

  <p>
    <a href="https://github.com/commensal/NoDpiTube/releases/latest">
      <img src="https://img.shields.io/github/v/release/commensal/NoDpiTube?style=for-the-badge&color=red&label=%D0%A1%D0%BA%D0%B0%D1%87%D0%B0%D1%82%D1%8C%20NoDpiTube" alt="Latest Release" />
    </a>
  </p>
</div>

---

## Что это

NoDpiTube — клиент YouTube для Android TV и Google TV. Внутри тот же SmartTube: без рекламы, с SponsorBlock, 4K, фоновым воспроизведением и обычными настройками плеера. Отличие в том, что обход замедления YouTube встроен в само приложение. Отдельный VPN, прокси на роутере или второе приложение не нужны.

В лаунчере оно называется **YouTube** и ставится рядом с официальным клиентом и оригинальным SmartTube: пакет `com.youtube.commensal`.

---

## Как устроен обход

Идея взята из [nodpi](https://github.com/theo0x0/nodpi) theo0x0: локальный прокси перехватывает TLS ClientHello и режет его так, чтобы фильтр провайдера не прочитал имя домена. [NoDPI4Android](https://github.com/GVCoder09/NoDPI4Android) — Android-оболочка вокруг того же метода, а не отдельный алгоритм. В это приложение перенесена только схема, не чужой APK.

Сейчас внутри три варианта. На одно соединение применяется один, они не складываются:

1. **Вариант 1.** Имя домена режется по 2 байта, первый кусок уходит с TTL=1. Обычно этого хватает.
2. **Вариант 2.** Та же нарезка, но без TTL. Нужен, если первый вариант сам рвёт соединение.
3. **Вариант 3.** Нарезка по одному байту, ближе к оригинальному скрипту. Имеет смысл, если провайдер склеивает короткие записи обратно.

Cloudflare не режется: для этих адресов фрагментация ломает и то, что и так открывается. Прокси сам занимает свободный порт, если 8881 уже занят. Root не нужен, слот VPN не занимается.

Обход не прячет IP от провайдера и не помогает, если адрес заблокирован по IP, а не по имени домена.

---

## Если видео не открывается

**Настройки → Основные → Сеть → Обход блокировок.**

Стоит вариант 1. Если ролик не стартует, переключитесь на 2 или 3 и запустите его заново: уже открытое соединение само не пересобирается. Отдельного пункта на главном экране нет, это одна настройка в разделе «Сеть».

Видео идёт через Chromium (Cronet), QUIC выключен, иначе поток ушёл бы мимо нарезки.

---

## Установка

Готовые файлы лежат в [Releases](https://github.com/commensal/NoDpiTube/releases/latest).

| Файл | Куда ставить |
| :--- | :--- |
| **universal.apk** | Почти любой телевизор, приставка или стик. Берите его, если не знаете архитектуру |
| **arm64-v8a.apk** | 64-битные приставки: Nvidia Shield, Ugoos, новые Google TV |
| **armeabi-v7a.apk** | 32-битные телевизоры и стики: Xiaomi Mi Box, Mi Stick и похожие |

Скачать можно прямо на телевизор через Downloader, перенести на флешке или отправить командой `adb install`. Уже установленная сборка с пакетом `com.youtube.commensal` обновляется поверх. Старая сборка с другим пакетом — это другое приложение, её можно удалить.

Новая версия предлагается на самом телевизоре.

---

## Лицензия

GPL-3.0, как у исходных проектов.

* Плеер: [SmartTube, yuliskov](https://github.com/yuliskov/SmartTube)
* Метод обхода: [nodpi, theo0x0](https://github.com/theo0x0/nodpi)
* Android-схема того же метода: [NoDPI4Android, GVCoder09](https://github.com/GVCoder09/NoDPI4Android)
