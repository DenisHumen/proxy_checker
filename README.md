# proxy_checker
## Скрипт для проверки работы http и socks5 прокси. Скрипт будет проверять такие параметры:
1. Статус подключения к прокси, успешное или нет (отметка ставится в колонке status)
2. ping к выбраным хостам (можно изменить в параметрах settings)
3. Скорость соединения (скачивание и выгрузка)
4. Так же поддерживается выгрузка данных в телеграм бота

## Установка
1. Нужно создать venv
```
python -m venv venv
```
```
source venv/bin/activate
```

## инструкция по подключения бота телеграмм
1.

## Общие настройки



2. Установка зависимостей

### Для работы скрипта нужна база mysql
```
CREATE TABLE `DATA`.`proxy_checker` (`id` INT NOT NULL AUTO_INCREMENT , `ip_address` TEXT NULL DEFAULT NULL , `port_http` TEXT NULL DEFAULT NULL , `port_socks5` TEXT NULL DEFAULT NULL , `status` TEXT NULL DEFAULT NULL , `speed_download` TEXT NULL DEFAULT NULL , `speed_upload` TEXT NULL DEFAULT NULL , `login` TEXT NULL DEFAULT NULL , `password` TEXT NULL DEFAULT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
```

## Запуск скрипта
1. 