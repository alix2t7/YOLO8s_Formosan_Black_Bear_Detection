"""
優化策略和搜索空間定義
"""

from typing import Any, Dict, List, Tuple

import optuna
from optuna.samplers import CmaEsSampler, RandomSampler, TPESampler


class SearchStrategies:
    """搜索策略管理器"""

    @staticmethod
    def get_bear_detection_search_space() -> Dict[str, Dict[str, Any]]:
        """獲取熊類檢測專用搜索空間"""
        return {
            "lr0": {"min": 1e-5, "max": 1e-2, "log": True, "description": "初始學習率"},
            "weight_decay": {
                "min": 1e-6,
                "max": 1e-2,
                "log": True,
                "description": "權重衰減",
            },
            "momentum": {"min": 0.8, "max": 0.99, "description": "動量"},
            "warmup_epochs": {"min": 1, "max": 10, "description": "預熱輪數"},
            "box": {"min": 5.0, "max": 15.0, "description": "邊界框損失權重"},
            "cls": {"min": 0.3, "max": 1.5, "description": "分類損失權重"},
            "dfl": {"min": 1.0, "max": 2.0, "description": "DFL損失權重"},
        }

    @staticmethod
    def get_sampler(
        strategy: str = "tpe", seed: int = 42
    ) -> optuna.samplers.BaseSampler:
        """獲取採樣器"""
        if strategy == "tpe":
            return TPESampler(seed=seed, n_startup_trials=10)
        elif strategy == "cmaes":
            return CmaEsSampler(seed=seed)
        elif strategy == "random":
            return RandomSampler(seed=seed)
        else:
            return TPESampler(seed=seed)

    @staticmethod
    def get_pruner(strategy: str = "median") -> optuna.pruners.BasePruner:
        """獲取剪枝器"""
        if strategy == "median":
            return optuna.pruners.MedianPruner(
                n_startup_trials=5, n_warmup_steps=30, interval_steps=10
            )
        elif strategy == "percentile":
            return optuna.pruners.PercentilePruner(
                percentile=25.0, n_startup_trials=5, n_warmup_steps=30
            )
        elif strategy == "hyperband":
            return optuna.pruners.HyperbandPruner(
                min_resource=10, max_resource=100, reduction_factor=3
            )
        else:
            return optuna.pruners.MedianPruner()

    @staticmethod
    def create_optimization_study(
        study_name: str = "bear_detection_optimization",
        strategy: str = "tpe",
        pruner_strategy: str = "median",
        seed: int = 42,
    ) -> optuna.Study:
        """創建優化研究"""
        sampler = SearchStrategies.get_sampler(strategy, seed)
        pruner = SearchStrategies.get_pruner(pruner_strategy)

        study = optuna.create_study(
            study_name=study_name, direction="maximize", sampler=sampler, pruner=pruner
        )

        return study

    @staticmethod
    def suggest_bear_parameters(trial: optuna.Trial) -> Dict[str, Any]:
        """為熊類檢測建議參數"""
        search_space = SearchStrategies.get_bear_detection_search_space()
        params = {}

        for param_name, config in search_space.items():
            if "min" in config and "max" in config:
                if isinstance(config["min"], int):
                    params[param_name] = trial.suggest_int(
                        param_name, config["min"], config["max"]
                    )
                else:
                    params[param_name] = trial.suggest_float(
                        param_name,
                        config["min"],
                        config["max"],
                        log=config.get("log", False),
                    )

        return params


class OptimizationMetrics:
    """優化指標計算"""

    @staticmethod
    def calculate_bear_detection_score(val_results) -> float:
        """計算熊類檢測分數"""
        try:
            if hasattr(val_results, "results_dict"):
                metrics = val_results.results_dict
            else:
                metrics = val_results

            # 主要指標
            map50 = metrics.get("metrics/mAP50(B)", 0.0)
            map50_95 = metrics.get("metrics/mAP50-95(B)", 0.0)
            precision = metrics.get("metrics/precision(B)", 0.0)
            recall = metrics.get("metrics/recall(B)", 0.0)

            # 備用指標名稱
            if map50 == 0.0:
                map50 = metrics.get("mAP50", 0.0)
            if map50_95 == 0.0:
                map50_95 = metrics.get("mAP50-95", 0.0)

            # 計算複合分數
            # 權重：mAP50 (40%), mAP50-95 (30%), precision (15%), recall (15%)
            score = 0.4 * map50 + 0.3 * map50_95 + 0.15 * precision + 0.15 * recall

            return float(score)

        except Exception:
            return 0.0

    @staticmethod
    def extract_training_metrics(results) -> Dict[str, float]:
        """提取訓練指標"""
        metrics = {}

        try:
            if hasattr(results, "results_dict"):
                raw_metrics = results.results_dict
            else:
                raw_metrics = results

            # 標準化指標名稱
            metric_mapping = {
                "mAP50": ["metrics/mAP50(B)", "mAP50"],
                "mAP50-95": ["metrics/mAP50-95(B)", "mAP50-95"],
                "precision": ["metrics/precision(B)", "precision"],
                "recall": ["metrics/recall(B)", "recall"],
                "train_loss": ["train/box_loss", "train_loss"],
                "val_loss": ["val/box_loss", "val_loss"],
            }

            for standard_name, possible_keys in metric_mapping.items():
                for key in possible_keys:
                    if key in raw_metrics:
                        metrics[standard_name] = float(raw_metrics[key])
                        break
                else:
                    metrics[standard_name] = 0.0

        except Exception:
            # 如果提取失敗，返回空指標
            metrics = {
                name: 0.0
                for name in [
                    "mAP50",
                    "mAP50-95",
                    "precision",
                    "recall",
                    "train_loss",
                    "val_loss",
                ]
            }

        return metrics
