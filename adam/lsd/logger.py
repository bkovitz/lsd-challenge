import logging
import sys
from typing import Any, cast

# Define custom log level for "TEST"
TEST_LEVEL = 25
logging.addLevelName(TEST_LEVEL, "TEST")

# ANSI terminal colors for different log levels
COLORS = {
    "DEBUG": "\033[94m",  # Bright Blue
    "INFO": "\033[92m",  # Bright Green
    "TEST": "\033[96m",  # Bright Cyan
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Bright Red
    "RESET": "\033[0m",  # Reset color
}


class ColorLogger(logging.Logger):
    """
    Custom logger class that adds color to log messages based on the log level.
    """

    def __init__(self, name: str, level: int = logging.NOTSET, prefix: str = "[App]") -> None:
        super().__init__(name, level)

    def format_message(self, level_name: str, msg: str) -> str:
        color = COLORS.get(level_name, "")
        reset = COLORS["RESET"]
        return f"{color}{msg}{reset}"

    def debug(self, msg: object, *args: Any, **kwargs: Any) -> None:
        super().debug(self.format_message("DEBUG", str(msg)), *args, **kwargs)

    def info(self, msg: object, *args: Any, **kwargs: Any) -> None:
        super().info(self.format_message("INFO", str(msg)), *args, **kwargs)

    def warning(self, msg: object, *args: Any, **kwargs: Any) -> None:
        super().warning(self.format_message("WARNING", str(msg)), *args, **kwargs)

    def error(self, msg: object, *args: Any, **kwargs: Any) -> None:
        super().error(self.format_message("ERROR", str(msg)), *args, **kwargs)

    def test(self, msg: object, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(TEST_LEVEL):
            self._log(TEST_LEVEL, self.format_message("TEST", str(msg)), args, **kwargs)


# Ensure that ColorLogger is used
logging.setLoggerClass(ColorLogger)


def get_logger(name=__name__, level=logging.DEBUG, prefix="[LSD]"):
    """
    Gets a logger instance with colorized output.

    Args:
        name (str): The name of the logger.
        level (int): The logging level (default is DEBUG).
        prefix (str): The prefix to include with each log message (default is "[LSD]").

    Returns:
        ColorLogger: The colorized logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    # Explicitly cast the logger to ColorLogger
    return cast(ColorLogger, logger)
