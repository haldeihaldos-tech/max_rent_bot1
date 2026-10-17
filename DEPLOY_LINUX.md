# Инструкция по переносу и запуску бота MAX на Linux (Ubuntu)

Эта инструкция поможет перенести ваш проект с Windows на стабильный Linux-сервер, чтобы избежать ошибок SSL.

## 1. Подготовка архива на Windows
1. Откройте папку `C:\root\max_rent_bot`.
2. Выделите все файлы внутри (`.env`, `main.py`, `bot.py`, `storage.py`, `texts.py`, `requirements.txt`).
3. Нажмите правой кнопкой мыши -> **Отправить** -> **Сжатая ZIP-папка**.
4. Создастся файл `max_rent_bot.zip`.

## 2. Подготовка сервера (Ubuntu/Debian)
Подключитесь к вашему серверу по SSH.

1. Обновите пакеты:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Установите Python и менеджер пакетов:
```bash
sudo apt install -y python3 python3-pip git unzip
```

3. Создайте папку для проекта:
```bash
mkdir -p ~/projects && cd ~/projects
```

## 3. Перенос файлов
Есть два способа:

### Способ А: Через SCP (если архив небольшой)
С вашего локального ПК (в новом терминале, не на сервере) выполните:
```bash
scp C:\root\max_rent_bot.zip user@ВАШ_IP_СЕРВЕРА:~/projects/
```
*(Замените `user` на имя пользователя сервера, например `ubuntu`)*

### Способ Б: Через Git (рекомендуется)
1. На сервере:
```bash
cd ~/projects
git clone https://github.com/ВАШ_ЛОГИН/ВАШ_РЕПОЗИТОРИЙ.git max_rent_bot
```
*(Загрузите ваш код в GitHub/GitLab с Windows заранее)*

## 4. Настройка на сервере
1. Зайдите в папку:
```bash
cd ~/projects/max_rent_bot
```

2. Распакуйте архив (если использовали Способ А):
```bash
unzip max_rent_bot.zip
```

3. Проверьте файл `.env`. Убедитесь, что в нем есть ваши данные:
```bash
cat .env
```
*(Должно быть: ACCESS_TOKEN=..., ADMIN_USER_ID=515597285, TARGET_CHANNEL_ID=-78791835305405)*

4. Создайте виртуальное окружение и установите зависимости:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Запуск
Запустите бота:
```bash
python main.py
```

Бот запустится в режиме Long Polling. Оставьте это окно терминала открытым или используйте утилиту `screen`/`tmux`, чтобы бот работал в фоне.

## 6. Проверка
1. Напишите боту в MAX `/start`.
2. Пройдите опрос.
3. На аккаунте администратора (515597285) должно прийти сообщение на модерацию.

## Остановка бота
Нажмите `Ctrl + C` в окне терминала, где запущен бот.