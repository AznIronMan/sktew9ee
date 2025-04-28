import inspect
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import socket
import sys


DEBUG_ENABLED = os.getenv("DEBUG", "false").lower() == "true"


class SKLogger:
    DATE_FORMAT: str = "%Y.%m.%d %H:%M:%S"

    def __init__(
        self,
        name: str = "custom_logger",
        log_cli: bool = True,
        log_file: bool = True,
        log_dir: str = "./.logs/",
        hostname: str = "default",
    ) -> None:
        logging.root.handlers = []
        self.logger = logging.getLogger(name)
        self.logger.handlers.clear()
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)
        self.hostname = hostname
        self.log_dir = log_dir
        if log_cli:
            cli_handler = logging.StreamHandler(sys.stdout)
            cli_handler.setLevel(
                logging.DEBUG if DEBUG_ENABLED else logging.INFO
            )
            formatter = self._create_formatter(use_colors=True, is_cli=True)
            cli_handler.setFormatter(formatter)
            self.logger.addHandler(cli_handler)
            self.debug("CLI logging initialized")
        if log_file:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            log_file_name = (
                f"{hostname}-{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler = logging.FileHandler(
                os.path.join(log_dir, log_file_name), mode="a"
            )
            file_handler.setLevel(
                logging.DEBUG if DEBUG_ENABLED else logging.INFO
            )
            file_handler.setFormatter(
                self._create_formatter(use_colors=False, is_cli=False)
            )
            self.logger.addHandler(file_handler)

    def _create_formatter(
        self, use_colors: bool = True, is_cli: bool = False
    ) -> logging.Formatter:
        return CustomFormatter(use_colors, is_cli)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)


class CustomFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[91m",  # Red
        "RESET": "\033[0m",  # Reset color
    }

    def __init__(self, use_colors: bool = True, is_cli: bool = False):
        super().__init__()
        self.use_colors = use_colors
        self.is_cli = is_cli

    def format(self, record: logging.LogRecord) -> str:
        try:
            frame = inspect.currentframe()
            frames = []
            while frame:
                frames.append(frame)
                frame = frame.f_back
            caller_frame = None
            for frame in frames:
                if (
                    frame.f_code.co_filename.endswith(
                        ("sk_logger.py", "logging/__init__.py")
                    )
                    or "logging" in frame.f_code.co_name
                ):
                    continue
                caller_frame = frame
                break
            if caller_frame:
                real_filename = os.path.basename(
                    caller_frame.f_code.co_filename
                )
                real_lineno = caller_frame.f_lineno
            else:
                real_filename = os.path.basename(record.pathname)
                real_lineno = record.lineno

            if self.use_colors:
                level_name = (
                    f"{self.COLORS.get(record.levelname, '')}"
                    f"{record.levelname}"
                    f"{self.COLORS['RESET']}"
                )
            else:
                level_name = record.levelname

            message = record.getMessage()
            if DEBUG_ENABLED and self.is_cli and len(message) > 400:
                message = f"{message[:200]}...{message[-200:]}"

            log_info = (
                f"[{datetime.now().strftime(SKLogger.DATE_FORMAT)}] | "
                f"[{level_name}] : "
                f"{real_filename}:{real_lineno} | "
                f"{message}"
            )
            return log_info
        except Exception as e:
            print(f"CustomFormatter format error: {e}")
            return str(record.getMessage())


_logger_instance: Optional[SKLogger] = None


def use_logger() -> SKLogger:
    global _logger_instance
    if _logger_instance is None:
        hostname = socket.gethostname().split(".")[0].lower()
        _logger_instance = SKLogger(hostname=hostname)
        if DEBUG_ENABLED:
            print("=== Logger Debug Info ===")
            print(f"Logger level: {_logger_instance.logger.level}")
            print(f"Handler count: {len(_logger_instance.logger.handlers)}")
            for idx, handler in enumerate(_logger_instance.logger.handlers):
                print(f"Handler {idx}: {type(handler)} Level: {handler.level}")
            print("======================")
    return _logger_instance


sk_log = use_logger()
