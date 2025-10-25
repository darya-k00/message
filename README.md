# Message bot
Телеграмм бот для отслеживания прогресса уроков 
## Установка
1. Скачайте репозиторий
2. Установите зависимости
```
pip install -r requirements.txt
```
3. Создайте файл ```.env``` и заполните его
```
DEWMAN_TOKEN = ваш токен
TELEGRAM_TOKEN = токен бота
TELEGRAM_CHAT_ID= id вашего чата
```
## Запуск
1 способ
```
python botik.py
```
2 способ с указанием chat_id
```
python botik.py --chat_id
```
