"""
YOLOv8s 訓練器 - 修復版本
整合所有訓練功能的統一界面
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import torch
import yaml
from ultralytics import YOLO


class YOLOv8sTrainer:
    """YOLOv8s 訓練器 - 簡化版本，基於原始代碼的核心功能"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化訓練器

        Args:
            config: 訓練配置字典
        """
        self.config = config

        # 從配置中提取核心參數
        model_config = config.get("model", {})
        training_config = config.get("training", {})

        # 核心配置
        self.model_size = model_config.get("name", "yolov8s")
        self.num_classes = model_config.get("num_classes", 2)
        self.img_size = model_config.get("input_size", 640)

        # 訓練配置
        self.epochs = training_config.get("epochs", 300)
        self.batch_size = training_config.get("batch_size", 64)
        self.patience = training_config.get("patience", 40)

        # 路徑配置
        self.data_yaml = "./data.yaml"
        self.project_dir = "./results/training"
        self.experiment_name = f"yolov8s_{self._get_timestamp()}"

        # 模型和狀態
        self.model = None
        self.best_params = None

    def _get_timestamp(self) -> str:
        """獲取時間戳"""
        from datetime import datetime

        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def setup_environment(self) -> bool:
        """設置訓練環境"""
        try:
            # 創建必要目錄
            Path(self.project_dir).mkdir(parents=True, exist_ok=True)

            # 檢查數據配置
            if not Path(self.data_yaml).exists():
                self._create_default_data_yaml()

            return True

        except Exception as e:
            print(f"❌ 環境設置失敗: {e}")
            return False

    def _create_default_data_yaml(self):
        """創建預設數據配置"""
        dataset_config = self.config.get("dataset", {})

        data_config = {
            "path": "./data",
            "train": "images/train",
            "val": "images/val",
            "test": "images/val",
            "nc": self.num_classes,
            "names": dataset_config.get("class_names", ["kumay", "not_kumay"]),
        }

        with open(self.data_yaml, "w", encoding="utf-8") as f:
            yaml.dump(data_config, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ 已創建數據配置: {self.data_yaml}")

    def load_model(self) -> bool:
        """載入模型"""
        try:
            model_path = f"{self.model_size}.pt"
            self.model = YOLO(model_path)
            print(f"✅ 模型已載入: {model_path}")
            return True

        except Exception as e:
            print(f"❌ 模型載入失敗: {e}")
            return False

    def load_best_params(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """載入最佳參數"""
        if params:
            self.best_params = params
            print("✅ 已載入傳入的最佳參數")
            return self.best_params

        # 嘗試從文件載入最佳參數
        best_params_paths = [
            "./config/best_params.yaml",
            "./results/optimization/best_params.yaml",
            f"{self.project_dir}/best_params.yaml",
        ]

        for path in best_params_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.best_params = yaml.safe_load(f)
                    print(f"✅ 已從 {path} 載入最佳參數")
                    return self.best_params
                except Exception as e:
                    print(f"⚠️  從 {path} 載入參數失敗: {e}")
                    continue

        # 使用預設最佳參數
        self.best_params = {
            "optimizer": "AdamW",
            "lr0": 0.00038,
            "lrf": 0.08,
            "momentum": 0.937,
            "weight_decay": 0.0006,
            "cos_lr": True,
            "warmup_epochs": 5.0,
            "cls": 1.2,
            "box": 0.05,
            "dfl": 1.5,
            "hsv_h": 0.015,
            "hsv_s": 0.7,
            "hsv_v": 0.4,
            "degrees": 5,
            "translate": 0.3,
            "scale": 0.24,
            "fliplr": 0.25,
            "flipud": 0,
            "mosaic": 0.125,
            "mixup": 0.08,
        }
        print("✅ 使用預設最佳參數")
        return self.best_params

    def setup_gpu_config(self) -> Dict[str, Any]:
        """設置GPU配置"""
        gpu_config = {
            "use_gpu": False,
            "device": "cpu",
            "multi_gpu": False,
            "device_ids": [0],
        }

        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_config.update(
                {
                    "use_gpu": True,
                    "device": "0",
                    "multi_gpu": gpu_count > 1,
                    "device_ids": list(range(gpu_count)),
                }
            )

            print(f"✅ 檢測到 {gpu_count} 個GPU")
        else:
            print("⚠️  未檢測到GPU，使用CPU模式")

        return gpu_config

    def _prepare_training_args(self) -> Dict[str, Any]:
        """準備訓練參數"""
        # 基礎參數
        train_args = {
            "data": self.data_yaml,
            "epochs": self.epochs,
            "imgsz": self.img_size,
            "batch": self.batch_size,
            "patience": self.patience,
            "project": self.project_dir,
            "name": self.experiment_name,
            "exist_ok": True,
            "plots": True,
            "verbose": True,
        }

        # GPU配置
        gpu_config = self.setup_gpu_config()
        if gpu_config["use_gpu"]:
            if gpu_config["multi_gpu"]:
                train_args["device"] = ",".join(map(str, gpu_config["device_ids"]))
            else:
                train_args["device"] = gpu_config["device"]
        else:
            train_args["device"] = "cpu"

        # 載入最佳參數
        if self.best_params:
            # 訓練參數
            for key in [
                "lr0",
                "lrf",
                "momentum",
                "weight_decay",
                "warmup_epochs",
                "cos_lr",
            ]:
                if key in self.best_params:
                    train_args[key] = self.best_params[key]

            # 損失函數權重
            for key in ["cls", "box", "dfl"]:
                if key in self.best_params:
                    train_args[key] = self.best_params[key]

            # 數據增強參數
            for key in [
                "hsv_h",
                "hsv_s",
                "hsv_v",
                "degrees",
                "translate",
                "scale",
                "fliplr",
                "flipud",
                "mosaic",
                "mixup",
            ]:
                if key in self.best_params:
                    train_args[key] = self.best_params[key]

        return train_args

    def train_model(self) -> Dict[str, Any]:
        """訓練模型"""
        try:
            # 確保模型已載入
            if not self.model:
                if not self.load_model():
                    raise RuntimeError("模型載入失敗")

            # 確保模型不是None
            if self.model is None:
                raise RuntimeError("模型對象為None")

            # 準備訓練參數
            train_args = self._prepare_training_args()

            # 執行訓練
            print(f"📊 訓練參數:")
            print(f"   模型: {self.model_size}")
            print(f"   輪數: {self.epochs}")
            print(f"   批次大小: {train_args.get('batch', self.batch_size)}")
            print(f"   圖片大小: {self.img_size}")

            results = self.model.train(**train_args)

            # 解析結果
            training_results = self._parse_results(results)

            print("✅ 訓練完成!")
            return training_results

        except Exception as e:
            print(f"❌ 訓練失敗: {e}")
            return {"success": False, "error": str(e)}

    def _parse_results(self, results) -> Dict[str, Any]:
        """解析訓練結果"""
        try:
            parsed_results = {
                "success": True,
                "model_path": getattr(results, "save_dir", None),
                "best_fitness": getattr(results, "best_fitness", None),
                "epochs_completed": getattr(results, "epoch", 0),
            }

            # 提取指標
            if hasattr(results, "results_dict"):
                parsed_results["metrics"] = results.results_dict

            return parsed_results

        except Exception as e:
            return {
                "success": False,
                "error": f"結果解析失敗: {e}",
                "raw_results": str(results),
            }

    def run_complete_training(self) -> Optional[Dict[str, Any]]:
        """執行完整訓練流程"""
        try:
            # 1. 設置環境
            if not self.setup_environment():
                return None

            # 2. 載入最佳參數
            self.load_best_params()

            # 3. 訓練模型
            training_result = self.train_model()

            if training_result.get("success", False):
                results = {
                    "training_result": training_result,
                    "model_size": self.model_size,
                    "experiment_name": self.experiment_name,
                    "project_dir": self.project_dir,
                }

                # 驗證模型
                validation_result = self._validate_model()
                if validation_result:
                    results["validation_result"] = validation_result

                # 導出模型
                export_result = self._export_model()
                if export_result:
                    results["export_result"] = export_result

                return results
            else:
                return None

        except Exception as e:
            print(f"❌ 完整訓練流程失敗: {e}")
            results = {"success": False, "error": str(e)}
            return results

    def _validate_model(self) -> Optional[Dict[str, Any]]:
        """驗證模型"""
        try:
            if self.model:
                results = self.model.val()
                return {"success": True, "validation_metrics": results}
        except Exception as e:
            print(f"⚠️  模型驗證失敗: {e}")
            return {"success": False, "error": str(e)}

    def _export_model(self) -> Optional[Dict[str, Any]]:
        """導出模型"""
        try:
            if self.model:
                export_path = self.model.export(format="onnx")
                return {"success": True, "export_path": export_path}
        except Exception as e:
            print(f"⚠️  模型導出失敗: {e}")
            return {"success": False, "error": str(e)}
