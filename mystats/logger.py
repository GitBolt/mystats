from datetime import datetime
from colorama import init
from termcolor import colored

COMMON_LOG_FORMAT: str = "%d/%b/%Y-%Hh:%Mm:%Ss"

init()


class Logger:
    @staticmethod
    def __log(color, log_type, message) -> None:
        date: str = datetime.now().strftime(COMMON_LOG_FORMAT)

        print(
            f"[{colored(date, 'magenta')}] [{colored(log_type, color=color)}]",
            message, flush=True
        )

    def success(self, message: str) -> None:
        self.__log('green', 'Success', message)

    def inform(self, message: str) -> None:
        self.__log('blue', 'Info', message)

    def warn(self, message: str) -> None:
        self.__log('yellow', 'Warning', message)

    def error(self, message: str, fatal: bool = True) -> None:
        self.__log('red', 'Error', message)

        if fatal:
            quit()


log = Logger()