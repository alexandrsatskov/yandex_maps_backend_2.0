
REST API сервис для Android приложения MVP проекта <**Новый пользовательский контент в Яндекс.Картах**>.

Привет, это мой некий выпускной проект - итог обучения в Яндекс академии летом 2к21 года, на направлении backend.

Это очень маленькое (в плане функциональности) API, но не такое маленькое в плане общей инфраструктуры.

В основе лежит **aiohttp**, для валидации используется довольно молодой **aiohttp-pydantic**, в качестве хранилища - **postgres**, и для доступа к БД любимая **SQLAlchemy**

Для общей автоматизации используется **make**, **docker**, **alembic**, **ansible**, **locust**

Что внутри?
-----------
Приложение упаковано в Docker-контейнер и разворачивается с помощью Ansible.

Внутри Docker-контейнера доступны две команды: **maps-db** — утилита
для управления состоянием базы данных и **maps-api** — утилита для 
запуска REST API сервиса.

Как использовать?
-----------------
Как применить миграции:

`docker run -it -e MAPS_PG_URL=postgresql+asyncpg://user:hackme@localhost/maps satskov/maps maps-db upgrade head`

Как запустить REST API сервис локально на порту 8081:

`docker run -it -p 8081:8081 -e MAPS_PG_URL=postgresql+asyncpg://user:hackme@localhost/maps satskov/maps`

Все доступные опции запуска любой команды можно получить с помощью
аргумента `--help`:

`docker run satskov/maps maps-db --help`

`docker run satskov/maps maps-api --help`

Опции для запуска можно указывать как аргументами командной строки, так и
переменными окружения с префиксом `MAPS` (например: вместо аргумента
`--pg-url` можно воспользоваться `MAPS_PG_URL`).

Как развернуть?
---------------
Чтобы развернуть и запустить сервис на серверах, добавьте список серверов в файл
deploy/hosts.ini (с установленной Ubuntu) и выполните команды:

`cd deploy`
`ansible-playbook -i hosts.ini --user=root deploy.yml`

Разработка
==========

Быстрые команды
---------------
* `make` Отобразить список доступных команд
* `make devenv` Создать и настроить виртуальное окружение для разработки
* `make postgres` Поднять Docker-контейнер с PostgreSQL
* `make lint` Проверить синтаксис и стиль кода с помощью `pylama`_
* `make clean` Удалить файлы, созданные модулем `distutils`_
* `make test` Запустить тесты
* `make sdist` Создать `source distribution`_
* `make docker` Собрать Docker-образ
* `make upload` Загрузить Docker-образ на hub.docker.com


Как подготовить окружение для разработки?
-----------------------------------------

    make devenv
    make postgres
    source env/bin/activate
    maps-db upgrade head
    maps-api

После запуска команд приложение начнет слушать запросы на 0.0.0.0:8081.

Как запустить тесты локально?
-----------------------------
    make devenv
    make postgres
    source env/bin/activate
    pytest


Как запустить нагрузочное тестирование?
---------------------------------------
Для запуска `locust` необходимо выполнить следующие команды:

    make devenv
    source env/bin/activate
    locust

После этого станет доступен веб-интерфейс по адресу http://localhost:8089

