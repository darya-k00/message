import os
import requests
import time
import logging
import traceback
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


def send_telegram_notification(telegram_token, chat_id, message):

    response = requests.post(
        f"https://api.telegram.org/bot{telegram_token}/sendMessage",
        json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        },
        timeout=5
    )
    response.raise_for_status()


def main():
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    try:
        telegram_token = os.environ['TELEGRAM_TOKEN']
        devman_token = os.environ['DEVMAN_TOKEN']
        chat_id = os.environ['TELEGRAM_CHAT_ID']
        logger.info("Запуск бота")
        send_telegram_notification(telegram_token, chat_id, "Бот запущен")

    except KeyError as e:
        error_msg = f"Ошибка отправки в Telegram {e}"
        logger.error(error_msg)
        send_telegram_notification(error_msg)
        return

    last_timestamp = None
    read_timeout_logged = False
    last_log_time = 0
    log_interval = 10

    while True:
        try:
            response = requests.get(
                "https://dvmn.org/api/long_polling/",
                headers={"Authorization": f"Token {devman_token}"},
                params={"timestamp": last_timestamp} if last_timestamp else {},
                timeout=90
            )
            response.raise_for_status()
            review_data = response.json()

            if review_data['status'] == 'found':
                lesson = review_data['new_attempts'][0]
                lesson_title = lesson['lesson_title']
                is_negative = lesson['is_negative']

                message = (
                    f"Проверили работу: {lesson_title} - "
                    f"{'Есть ошибки, которые нужно исправить' if is_negative else 'Работа принята!'}"
                )
                response = requests.post(
                    f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                    json={'chat_id': chat_id, 'text': message},
                    timeout=10
                )
                response.raise_for_status()
                logger.info(f"Сообщение: {message}")
                last_timestamp = review_data['last_attempt_timestamp']
            else:
                last_timestamp = review_data['timestamp_to_request']

        except requests.exceptions.ReadTimeout:

            continue

        except requests.exceptions.ConnectionError:
            error_msg = "Ошибка подключения к интернету"
            logger.warning(error_msg)
            send_telegram_notification(error_msg)
            time.sleep(30)

        except Exception as e:
            error_traceback = traceback.format_exc()
            error_msg = f"ошибка:\n```\n{error_traceback}\n```"

            logger.critical(error_msg)



if __name__ == '__main__':
    main()
