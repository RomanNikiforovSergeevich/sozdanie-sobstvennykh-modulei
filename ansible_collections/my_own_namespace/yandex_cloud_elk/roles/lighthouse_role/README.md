# Ansible Role: Lighthouse

Эта роль устанавливает веб-сервер Nginx и разворачивает на нём статический веб-интерфейс [LightHouse](https://github.com/VKCOM/lighthouse) для работы с ClickHouse.

## Требования (Requirements)

*   Целевая ОС: Ubuntu 20.04/22.04 или Debian 11/12.

## Переменные роли (Role Variables)

Переменные, которые можно переопределить (расположены в `defaults/main.yml`)

Что делает роль

    Устанавливает пакеты nginx и unzip.

    Скачивает архив с исходным кодом LightHouse.

    Распаковывает архив в директорию lighthouse_web_root.

    Создает символическую ссылку для удобства (по умолчанию /var/www/lighthouse).

    Генерирует конфигурационный файл Nginx из шаблона nginx.conf.j2 и применяет его.

    Активирует сайт в Nginx и удаляет дефолтную конфигурацию.

    Запускает Nginx и перезапускает его при изменении конфигурации.

Включение роли в плейбук:

```yaml

- hosts: lighthouse
  become: true
  roles:
    - lighthouse
