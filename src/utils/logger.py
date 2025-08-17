"""
日誌系統模組
提供統一的日誌管理功能
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union


class ColoredFormatter(logging.Formatter):
    """彩色日誌格式化器"""

    # 顏色代碼
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 綠色
        "WARNING": "\033[33m",  # 黃色
        "ERROR": "\033[31m",  # 紅色
        "CRITICAL": "\033[35m",  # 紫色
        "RESET": "\033[0m",  # 重置
    }

    def format(self, record):
        # 獲取原始格式化結果
        original = super().format(record)

        # 添加顏色
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        return f"{color}{original}{reset}"


class YOLOLogger:
    """YOLOv8s 專用日誌器"""

    def __init__(self, name: str = "YOLOv8s", level: str = "INFO"):
        self.name = name
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # 避免重複添加處理器
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """設置日誌處理器"""
        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # 彩色格式化器
        colored_formatter = ColoredFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(colored_formatter)

        self.logger.addHandler(console_handler)

    def add_file_handler(self, log_file: Union[str, Path], level: str = "DEBUG"):
        """添加文件處理器"""
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper()))

        # 文件格式化器（不使用顏色）
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        self.logger.addHandler(file_handler)

    def info(self, message: str, **kwargs):
        """信息日誌"""
        self.logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """調試日誌"""
        self.logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """警告日誌"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """錯誤日誌"""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """嚴重錯誤日誌"""
        self.logger.critical(message, **kwargs)

    def log_config(self, config: Dict[str, Any], title: str = "配置信息"):
        """記錄配置信息"""
        self.info(f"=== {title} ===")
        for key, value in config.items():
            self.info(f"  {key}: {value}")
        self.info("=" * (len(title) + 8))

    def log_system_info(self):
        """記錄系統信息"""
        import platform

        import psutil

        self.info("=== 系統信息 ===")
        self.info(f"  操作系統: {platform.system()} {platform.release()}")
        self.info(f"  Python 版本: {platform.python_version()}")
        self.info(f"  CPU 核心數: {psutil.cpu_count()}")
        self.info(f"  總記憶體: {psutil.virtual_memory().total / 1024**3:.1f} GB")

        # GPU 信息
        try:
            import torch

            if torch.cuda.is_available():
                self.info(f"  GPU 數量: {torch.cuda.device_count()}")
                for i in range(torch.cuda.device_count()):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = (
                        torch.cuda.get_device_properties(i).total_memory / 1024**3
                    )
                    self.info(f"    GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
            else:
                self.info("  GPU: 不可用")
        except ImportError:
            self.info("  GPU: 無法檢測 (PyTorch 未安裝)")

        self.info("=" * 16)

    def log_training_start(self, config: Dict[str, Any]):
        """記錄訓練開始"""
        self.info("🚀 " + "=" * 50)
        self.info("🚀 YOLOv8s 黑熊辨識訓練開始")
        self.info("🚀 " + "=" * 50)

        self.log_config(config, "訓練配置")
        self.log_system_info()

    def log_training_end(self, success: bool, duration: float):
        """記錄訓練結束"""
        status = "成功完成" if success else "異常結束"
        emoji = "🎉" if success else "❌"

        self.info(f"{emoji} " + "=" * 50)
        self.info(f"{emoji} 訓練{status}")
        self.info(f"{emoji} 總耗時: {duration:.2f} 秒 ({duration / 3600:.2f} 小時)")
        self.info(f"{emoji} " + "=" * 50)

    def log_optimization_start(self, n_trials: int):
        """記錄優化開始"""
        self.info("🎯 " + "=" * 50)
        self.info("🎯 超參數優化開始")
        self.info(f"🎯 目標試驗數: {n_trials}")
        self.info("🎯 " + "=" * 50)

    def log_trial_result(self, trial_number: int, score: float, params: Dict[str, Any]):
        """記錄試驗結果"""
        self.info(f"✅ Trial {trial_number:3d} | Score: {score:.4f}")
        self.debug(f"   參數: {params}")

    def log_best_params(self, best_params: Dict[str, Any], best_score: float):
        """記錄最佳參數"""
        self.info("🏆 " + "=" * 50)
        self.info("🏆 最佳參數找到")
        self.info(f"🏆 最佳分數: {best_score:.4f}")
        self.info("🏆 " + "=" * 50)
        self.log_config(best_params, "最佳參數")


# 全域日誌器實例
_global_logger: Optional[YOLOLogger] = None


def setup_logger(
    name: str = "YOLOv8s",
    level: str = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    log_dir: Optional[Union[str, Path]] = None,
) -> YOLOLogger:
    """
    設置日誌器

    Args:
        name: 日誌器名稱
        level: 日誌級別
        log_file: 日誌文件路徑
        log_dir: 日誌目錄 (如果指定，會自動生成文件名)

    Returns:
        YOLOLogger: 日誌器實例
    """
    global _global_logger

    logger = YOLOLogger(name, level)

    # 設置文件日誌
    if log_file or log_dir:
        if log_dir and not log_file:
            # 自動生成日誌文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = Path(log_dir) / f"yolov8s_{timestamp}.log"

        if log_file:
            logger.add_file_handler(log_file)
            logger.info(f"日誌文件: {log_file}")

    _global_logger = logger
    return logger


def get_logger() -> YOLOLogger:
    """
    獲取全域日誌器

    Returns:
        YOLOLogger: 日誌器實例
    """
    global _global_logger

    if _global_logger is None:
        _global_logger = setup_logger()

    return _global_logger


def suppress_warnings():
    """抑制常見警告"""
    import os
    import warnings

    # 抑制各種警告
    warnings.filterwarnings("ignore", ".*iCCP.*", UserWarning)
    warnings.filterwarnings("ignore", ".*known incorrect sRGB profile.*", UserWarning)
    warnings.filterwarnings("ignore", ".*Corrupt EXIF data.*", UserWarning)

    # 設置環境變數
    os.environ["PYTHONWARNINGS"] = "ignore::UserWarning"
    os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

    # PIL 警告抑制
    try:
        from PIL import Image

        Image.MAX_IMAGE_PIXELS = None
    except (ImportError, AttributeError):
        pass

    get_logger().info("✅ 警告抑制已設置")


# 便捷函數
def log_info(message: str):
    """快速記錄信息"""
    get_logger().info(message)


def log_error(message: str):
    """快速記錄錯誤"""
    get_logger().error(message)


def log_warning(message: str):
    """快速記錄警告"""
    get_logger().warning(message)
