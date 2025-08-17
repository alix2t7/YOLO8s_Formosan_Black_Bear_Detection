"""
數據加載器和預處理
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yaml


class DataLoader:
    """數據加載器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dataset_config = config.get("dataset", {})

    def setup_dataset(self) -> bool:
        """設置數據集"""
        try:
            # 檢查數據集路徑
            dataset_path = self.dataset_config.get("path")
            if not dataset_path or not os.path.exists(dataset_path):
                print(f"❌ 數據集路徑不存在: {dataset_path}")
                return False

            # 檢查必需的目錄結構
            required_dirs = ["images/train", "images/val", "labels/train", "labels/val"]
            for dir_name in required_dirs:
                dir_path = os.path.join(dataset_path, dir_name)
                if not os.path.exists(dir_path):
                    print(f"❌ 必需目錄不存在: {dir_path}")
                    return False

            # 檢查配置文件
            config_path = self.dataset_config.get("config_path")
            if not config_path or not os.path.exists(config_path):
                print(f"❌ 數據集配置文件不存在: {config_path}")
                return False

            print("✅ 數據集檢查通過")
            return True

        except Exception as e:
            print(f"❌ 數據集設置失敗: {str(e)}")
            return False

    def get_dataset_info(self) -> Dict[str, Any]:
        """獲取數據集信息"""
        info = {
            "train_images": 0,
            "val_images": 0,
            "train_labels": 0,
            "val_labels": 0,
            "classes": [],
            "class_distribution": {},
        }

        try:
            dataset_path = self.dataset_config.get("path")

            # 計算圖像數量
            train_images_dir = os.path.join(dataset_path, "images/train")
            val_images_dir = os.path.join(dataset_path, "images/val")

            if os.path.exists(train_images_dir):
                info["train_images"] = len(
                    [
                        f
                        for f in os.listdir(train_images_dir)
                        if f.lower().endswith((".jpg", ".jpeg", ".png"))
                    ]
                )

            if os.path.exists(val_images_dir):
                info["val_images"] = len(
                    [
                        f
                        for f in os.listdir(val_images_dir)
                        if f.lower().endswith((".jpg", ".jpeg", ".png"))
                    ]
                )

            # 計算標籤數量
            train_labels_dir = os.path.join(dataset_path, "labels/train")
            val_labels_dir = os.path.join(dataset_path, "labels/val")

            if os.path.exists(train_labels_dir):
                info["train_labels"] = len(
                    [f for f in os.listdir(train_labels_dir) if f.endswith(".txt")]
                )

            if os.path.exists(val_labels_dir):
                info["val_labels"] = len(
                    [f for f in os.listdir(val_labels_dir) if f.endswith(".txt")]
                )

            # 讀取類別信息
            config_path = self.dataset_config.get("config_path")
            if config_path and os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    dataset_config = yaml.safe_load(f)
                    info["classes"] = dataset_config.get("names", [])

        except Exception as e:
            print(f"⚠️  獲取數據集信息失敗: {str(e)}")

        return info

    def validate_dataset(self) -> Tuple[bool, List[str]]:
        """驗證數據集"""
        errors = []

        try:
            dataset_path = self.dataset_config.get("path")

            # 檢查圖像和標籤對應關係
            for split in ["train", "val"]:
                images_dir = os.path.join(dataset_path, f"images/{split}")
                labels_dir = os.path.join(dataset_path, f"labels/{split}")

                if not os.path.exists(images_dir):
                    errors.append(f"圖像目錄不存在: {images_dir}")
                    continue

                if not os.path.exists(labels_dir):
                    errors.append(f"標籤目錄不存在: {labels_dir}")
                    continue

                # 獲取圖像文件
                image_files = [
                    f
                    for f in os.listdir(images_dir)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))
                ]

                # 檢查標籤文件
                for image_file in image_files[:10]:  # 檢查前10個文件
                    label_file = os.path.splitext(image_file)[0] + ".txt"
                    label_path = os.path.join(labels_dir, label_file)

                    if not os.path.exists(label_path):
                        errors.append(f"標籤文件缺失: {label_path}")

            # 檢查配置文件格式
            config_path = self.dataset_config.get("config_path")
            if config_path and os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                    required_keys = ["train", "val", "nc", "names"]
                    for key in required_keys:
                        if key not in config:
                            errors.append(f"配置文件缺少必需字段: {key}")

        except Exception as e:
            errors.append(f"驗證過程出錯: {str(e)}")

        return len(errors) == 0, errors


class DataPreprocessor:
    """數據預處理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def create_kaggle_dataset_config(self, dataset_path: str, output_path: str) -> str:
        """為 Kaggle 環境創建數據集配置"""
        config = {
            "path": dataset_path,
            "train": os.path.join(dataset_path, "images/train"),
            "val": os.path.join(dataset_path, "images/val"),
            "nc": 2,  # 熊類檢測：kumay, not_kumay
            "names": ["kumay", "not_kumay"],
        }

        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 保存配置
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        return output_path

    def check_image_formats(self, dataset_path: str) -> Dict[str, Any]:
        """檢查圖像格式"""
        formats = {}
        total_images = 0

        for split in ["train", "val"]:
            images_dir = os.path.join(dataset_path, f"images/{split}")
            if not os.path.exists(images_dir):
                continue

            for file in os.listdir(images_dir):
                if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
                    ext = os.path.splitext(file)[1].lower()
                    formats[ext] = formats.get(ext, 0) + 1
                    total_images += 1

        return {
            "formats": formats,
            "total_images": total_images,
            "supported": all(
                ext in [".jpg", ".jpeg", ".png"] for ext in formats.keys()
            ),
        }

    def prepare_for_training(self, base_path: str) -> bool:
        """為訓練準備數據"""
        try:
            # 檢查並創建必要目錄
            required_dirs = [
                "results/training",
                "results/optimization",
                "checkpoints",
                "logs",
            ]

            for dir_name in required_dirs:
                dir_path = os.path.join(base_path, dir_name)
                os.makedirs(dir_path, exist_ok=True)

            print("✅ 訓練目錄準備完成")
            return True

        except Exception as e:
            print(f"❌ 準備訓練目錄失敗: {str(e)}")
            return False


class DataAnalyzer:
    """數據分析器"""

    @staticmethod
    def analyze_label_distribution(dataset_path: str) -> Dict[str, Any]:
        """分析標籤分佈"""
        distribution = {
            "train": {"kumay": 0, "not_kumay": 0},
            "val": {"kumay": 0, "not_kumay": 0},
        }

        try:
            for split in ["train", "val"]:
                labels_dir = os.path.join(dataset_path, f"labels/{split}")
                if not os.path.exists(labels_dir):
                    continue

                for label_file in os.listdir(labels_dir):
                    if not label_file.endswith(".txt"):
                        continue

                    label_path = os.path.join(labels_dir, label_file)

                    try:
                        with open(label_path, "r") as f:
                            lines = f.readlines()

                        for line in lines:
                            if line.strip():
                                class_id = int(line.split()[0])
                                if class_id == 0:
                                    distribution[split]["kumay"] += 1
                                elif class_id == 1:
                                    distribution[split]["not_kumay"] += 1
                    except:
                        continue

        except Exception as e:
            print(f"⚠️  分析標籤分佈失敗: {str(e)}")

        return distribution

    @staticmethod
    def get_dataset_statistics(dataset_path: str) -> Dict[str, Any]:
        """獲取數據集統計信息"""
        stats = {
            "image_count": {},
            "label_distribution": {},
            "file_sizes": {},
            "image_dimensions": {},
        }

        try:
            # 圖像數量統計
            for split in ["train", "val"]:
                images_dir = os.path.join(dataset_path, f"images/{split}")
                if os.path.exists(images_dir):
                    image_files = [
                        f
                        for f in os.listdir(images_dir)
                        if f.lower().endswith((".jpg", ".jpeg", ".png"))
                    ]
                    stats["image_count"][split] = len(image_files)
                else:
                    stats["image_count"][split] = 0

            # 標籤分佈
            stats["label_distribution"] = DataAnalyzer.analyze_label_distribution(
                dataset_path
            )

        except Exception as e:
            print(f"⚠️  獲取數據集統計失敗: {str(e)}")

        return stats
