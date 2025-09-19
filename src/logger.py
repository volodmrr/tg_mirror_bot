import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name: str = "mirror", log_dir: str = "logs", log_file: str = "mirror.log") -> logging.Logger:
    base_dir = Path(__file__).resolve().parent
    log_dir_path = base_dir / log_dir
    log_dir_path.mkdir(exist_ok=True)

    log_path = log_dir_path / log_file

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    # file handler (with rotation)
    fh = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    # stdout handler (so journalctl sees logs)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)

    # Avoid duplicate handlers if reloaded
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(sh)

    # Quiet down Telethon spam
    logging.getLogger("telethon").setLevel(logging.WARNING)

    return logger

logger = setup_logger()