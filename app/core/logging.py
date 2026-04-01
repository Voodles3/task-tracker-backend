import logging


def setup_logging() -> None:
    class ColorFormatter(logging.Formatter):
        COLORS = {
            "DEBUG": "\033[94m",  # Blue
            "INFO": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "CRITICAL": "\033[95m",  # Magenta
        }
        RESET = "\033[0m"

        def format(self, record):
            color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            record.module = f"{color}{record.module}{self.RESET}"
            return super().format(record)

    handler = logging.StreamHandler()
    handler.setFormatter(
        ColorFormatter(
            fmt="[%(asctime)s] %(levelname)s (%(module)s): %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)
