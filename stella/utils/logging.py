import logging


def set_logging(level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [STELLA] %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
