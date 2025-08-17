"""
YOLOv8s 完整訓練管道
版本: 1.0.0
日期: 2025-08-08

主要模組：
- environment: 環境管理
- optimization: 超參數優化
- training: 模型訓練
- data: 數據處理
- utils: 通用工具
"""

__version__ = "1.0.0"
__author__ = "YOLOv8s Pipeline Contributors"
__description__ = "YOLOv8s 黑熊辨識完整訓練管道"

# 版本兼容性檢查
import sys
if sys.version_info < (3, 8):
    raise RuntimeError("需要 Python 3.8 或更高版本")

# 導入核心模組
from .utils import logger, gpu_manager, file_manager
from .environment import setup, manager
from .data import loader, validator
from .optimization import optuna_optimizer, search_strategies
from .training import trainer, callbacks, utils as training_utils

# 模組可用性檢查
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import ultralytics
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

# 功能可用性報告
def check_dependencies():
    """檢查依賴套件可用性"""
    deps = {
        "torch": TORCH_AVAILABLE,
        "ultralytics": ULTRALYTICS_AVAILABLE, 
        "optuna": OPTUNA_AVAILABLE
    }
    
    print("=== 依賴套件檢查 ===")
    for name, available in deps.items():
        status = "✅" if available else "❌"
        print(f"{status} {name}: {'可用' if available else '不可用'}")
    
    return all(deps.values())

# 快速配置函數
def quick_setup():
    """快速設置管道環境"""
    print("🚀 YOLOv8s 訓練管道初始化中...")
    
    if not check_dependencies():
        print("❌ 依賴套件檢查失敗，請安裝所需套件")
        return False
    
    print("✅ 依賴套件檢查通過")
    return True

# 模組導出
__all__ = [
    # 版本信息
    "__version__", "__author__", "__description__",
    
    # 核心模組
    "logger", "gpu_manager", "file_manager",
    "setup", "manager",
    "loader", "validator", 
    "optuna_optimizer", "search_strategies",
    "trainer", "callbacks", "training_utils",
    
    # 工具函數
    "check_dependencies", "quick_setup"
]
