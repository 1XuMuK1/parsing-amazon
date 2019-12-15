import time

import schedule

from application.helpers.tasks import automatic_parsing_task


def main():
    schedule.every().day.at('05:15').do(automatic_parsing_task)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()
