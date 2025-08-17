"""
訓練回調函數
"""

from typing import Dict, Any, Callable, List
import time
from datetime import datetime


class TrainingCallbacks:
    """訓練回調管理器"""

    def __init__(self):
        self.callbacks = {
            "on_epoch_start": [],
            "on_epoch_end": [],
            "on_batch_start": [],
            "on_batch_end": [],
            "on_training_start": [],
            "on_training_end": [],
        }

        self.metrics_history = []
        self.start_time = None

    def add_callback(self, event: str, callback: Callable):
        """添加回調函數"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def trigger_callbacks(self, event: str, *args, **kwargs):
        """觸發回調函數"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"⚠️  回調函數錯誤: {e}")

    def log_metrics(self, epoch: int, metrics: Dict[str, float]):
        """記錄指標"""
        entry = {
            "epoch": epoch,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        }
        self.metrics_history.append(entry)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """獲取指標摘要"""
        if not self.metrics_history:
            return {}

        # 計算平均值和最佳值
        summary = {}
        for entry in self.metrics_history:
            for metric, value in entry["metrics"].items():
                if metric not in summary:
                    summary[metric] = {"values": [], "best": value, "avg": 0}

                summary[metric]["values"].append(value)
                if value > summary[metric]["best"]:
                    summary[metric]["best"] = value

        # 計算平均值
        for metric in summary:
            values = summary[metric]["values"]
            summary[metric]["avg"] = sum(values) / len(values)

        return summary
