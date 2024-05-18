import logging
from colorlog import ColoredFormatter


color_formatter = ColoredFormatter(
    "%(yellow)s%(asctime)-8s%(reset)s - %(log_color)s%(levelname)-1s%(reset)s - %(message)s",
    datefmt="%H:%M:%S",
    log_colors={
        "DEBUG": "white",
        "INFO": "green",
        "WARNING": "light_yellow",
        "ERROR": "bold_red",
        "CRITICAL": "red,bg_white",
    },
)
simple_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s -%(message)s (%(filename)s:%(lineno)d)",
    datefmt="%H:%M:%S",
)

handler = logging.StreamHandler()
handler.setFormatter(color_formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
