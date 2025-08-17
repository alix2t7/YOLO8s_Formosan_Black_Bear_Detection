"""
GPU 管理模組
提供GPU檢測、配置和優化功能
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch


class GPUManager:
    """GPU 管理器"""

    def __init__(self):
        self.cuda_available = torch.cuda.is_available()
        self.gpu_count = torch.cuda.device_count() if self.cuda_available else 0
        self.gpu_info = self._get_gpu_info() if self.cuda_available else []

    def get_device(self) -> str:
        """獲取推薦的設備字符串"""
        if self.cuda_available and self.gpu_count > 0:
            # 使用第一個可用的GPU
            return "0"
        else:
            return "cpu"

    def _get_gpu_info(self) -> List[Dict[str, Any]]:
        """獲取GPU詳細信息"""
        gpu_info = []

        for i in range(self.gpu_count):
            try:
                props = torch.cuda.get_device_properties(i)
                info = {
                    "id": i,
                    "name": props.name,
                    "total_memory": props.total_memory,
                    "total_memory_gb": props.total_memory / 1024**3,
                    "major": props.major,
                    "minor": props.minor,
                    "multi_processor_count": props.multi_processor_count,
                    "available": True,
                }

                # 獲取當前記憶體使用情況
                torch.cuda.set_device(i)
                allocated = torch.cuda.memory_allocated(i)
                reserved = torch.cuda.memory_reserved(i)

                info.update(
                    {
                        "allocated_memory": allocated,
                        "allocated_memory_gb": allocated / 1024**3,
                        "reserved_memory": reserved,
                        "reserved_memory_gb": reserved / 1024**3,
                        "free_memory": props.total_memory - allocated,
                        "free_memory_gb": (props.total_memory - allocated) / 1024**3,
                        "utilization": allocated / props.total_memory * 100,
                    }
                )

                gpu_info.append(info)

            except Exception as e:
                gpu_info.append(
                    {"id": i, "name": "Unknown", "error": str(e), "available": False}
                )

        return gpu_info

    def get_nvidia_smi_info(self) -> Optional[Dict[str, Any]]:
        """通過 nvidia-smi 獲取GPU信息"""
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            lines = result.stdout.strip().split("\n")
            smi_info = []

            for line in lines:
                parts = [part.strip() for part in line.split(",")]
                if len(parts) >= 6:
                    smi_info.append(
                        {
                            "index": int(parts[0]),
                            "name": parts[1],
                            "memory_total_mb": int(parts[2]),
                            "memory_used_mb": int(parts[3]),
                            "memory_free_mb": int(parts[4]),
                            "utilization_percent": int(parts[5]),
                        }
                    )

            return {"gpus": smi_info, "available": True}

        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            return None

    def print_gpu_info(self):
        """打印GPU信息"""
        print("=== GPU 信息 ===")

        if not self.cuda_available:
            print("❌ CUDA 不可用")
            return

        print(f"✅ CUDA 可用，檢測到 {self.gpu_count} 個GPU")

        for gpu in self.gpu_info:
            if gpu.get("available", False):
                print(f"\n🔹 GPU {gpu['id']}: {gpu['name']}")
                print(f"   總記憶體: {gpu['total_memory_gb']:.1f} GB")
                print(f"   已分配: {gpu['allocated_memory_gb']:.2f} GB")
                print(f"   已保留: {gpu['reserved_memory_gb']:.2f} GB")
                print(f"   可用: {gpu['free_memory_gb']:.2f} GB")
                print(f"   使用率: {gpu['utilization']:.1f}%")
                print(f"   計算能力: {gpu['major']}.{gpu['minor']}")
                print(f"   多處理器: {gpu['multi_processor_count']}")
            else:
                print(f"\n❌ GPU {gpu['id']}: 不可用")
                if "error" in gpu:
                    print(f"   錯誤: {gpu['error']}")

        # nvidia-smi 信息
        smi_info = self.get_nvidia_smi_info()
        if smi_info:
            print(f"\n📊 nvidia-smi 即時狀態:")
            for gpu in smi_info["gpus"]:
                print(
                    f"   GPU {gpu['index']}: {gpu['utilization_percent']}% 使用率, "
                    f"{gpu['memory_used_mb']}/{gpu['memory_total_mb']} MB 記憶體"
                )

    def get_optimal_device_setup(
        self, preferred_gpus: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """獲取最佳設備配置"""
        config = {
            "use_multi_gpu": False,
            "device_ids": [0],
            "strategy": "cpu",
            "available_memory_gb": 0,
            "recommended_batch_multiplier": 1,
        }

        if not self.cuda_available or self.gpu_count == 0:
            config["strategy"] = "cpu"
            return config

        # 篩選可用GPU
        available_gpus = [gpu for gpu in self.gpu_info if gpu.get("available", False)]

        if not available_gpus:
            config["strategy"] = "cpu"
            return config

        # 如果指定了優先GPU，先檢查可用性
        if preferred_gpus:
            valid_preferred = [
                gpu for gpu in available_gpus if gpu["id"] in preferred_gpus
            ]
            if valid_preferred:
                available_gpus = valid_preferred

        # 按記憶體大小排序
        available_gpus.sort(key=lambda x: x["free_memory_gb"], reverse=True)

        # 單GPU配置
        best_gpu = available_gpus[0]
        config.update(
            {
                "strategy": "single-gpu",
                "device_ids": [best_gpu["id"]],
                "available_memory_gb": best_gpu["free_memory_gb"],
                "recommended_batch_multiplier": 1,
            }
        )

        # 多GPU配置檢查
        if len(available_gpus) >= 2:
            # 檢查前兩個GPU是否記憶體相近
            gpu1, gpu2 = available_gpus[0], available_gpus[1]
            memory_diff = abs(gpu1["total_memory_gb"] - gpu2["total_memory_gb"])

            if memory_diff < 2.0:  # 記憶體差異小於2GB
                config.update(
                    {
                        "use_multi_gpu": True,
                        "strategy": "multi-gpu",
                        "device_ids": [gpu1["id"], gpu2["id"]],
                        "available_memory_gb": min(
                            gpu1["free_memory_gb"], gpu2["free_memory_gb"]
                        ),
                        "recommended_batch_multiplier": 2,
                    }
                )

        return config

    def setup_cuda_environment(self, device_ids: List[int]) -> bool:
        """設置CUDA環境"""
        if not self.cuda_available:
            return False

        try:
            # 設置可見GPU
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(map(str, device_ids))

            # 預熱GPU
            for device_id in device_ids:
                if device_id < self.gpu_count:
                    torch.cuda.set_device(device_id)
                    # 簡單的記憶體測試
                    test_tensor = torch.rand(100, 100).cuda()
                    del test_tensor
                    torch.cuda.empty_cache()

            return True

        except Exception as e:
            print(f"❌ CUDA環境設置失敗: {e}")
            return False

    def clear_gpu_memory(self, device_ids: Optional[List[int]] = None):
        """清理GPU記憶體"""
        if not self.cuda_available:
            return

        if device_ids is None:
            device_ids = list(range(self.gpu_count))

        for device_id in device_ids:
            try:
                torch.cuda.set_device(device_id)
                torch.cuda.empty_cache()
            except Exception as e:
                print(f"⚠️  清理GPU {device_id} 記憶體失敗: {e}")

    def monitor_gpu_usage(self) -> Dict[str, Any]:
        """監控GPU使用情況"""
        if not self.cuda_available:
            return {"available": False}

        usage_info = {"available": True, "gpus": []}

        for i in range(self.gpu_count):
            try:
                torch.cuda.set_device(i)
                allocated = torch.cuda.memory_allocated(i)
                reserved = torch.cuda.memory_reserved(i)
                total = torch.cuda.get_device_properties(i).total_memory

                gpu_usage = {
                    "id": i,
                    "allocated_gb": allocated / 1024**3,
                    "reserved_gb": reserved / 1024**3,
                    "total_gb": total / 1024**3,
                    "free_gb": (total - allocated) / 1024**3,
                    "utilization_percent": allocated / total * 100,
                }

                usage_info["gpus"].append(gpu_usage)

            except Exception as e:
                usage_info["gpus"].append({"id": i, "error": str(e)})

        return usage_info

    def get_recommended_batch_size(
        self, model_size: str, img_size: int, device_ids: List[int]
    ) -> int:
        """根據GPU配置推薦批次大小"""
        if not self.cuda_available:
            return 4  # CPU模式使用小批次

        # 基礎批次大小配置
        base_batch_sizes = {
            "yolov8n": {"640": 128, "512": 192, "320": 256},
            "yolov8s": {"640": 64, "512": 96, "320": 128},
            "yolov8m": {"640": 32, "512": 48, "320": 64},
            "yolov8l": {"640": 16, "512": 24, "320": 32},
            "yolov8x": {"640": 8, "512": 12, "320": 16},
        }

        # 獲取基礎批次大小
        base_batch = base_batch_sizes.get(model_size, {}).get(str(img_size), 32)

        # 根據GPU數量調整
        gpu_count = len(device_ids)

        if gpu_count >= 2:
            # 多GPU可以使用更大批次
            return base_batch * gpu_count
        else:
            # 單GPU，檢查記憶體
            if device_ids[0] < len(self.gpu_info):
                gpu = self.gpu_info[device_ids[0]]
                memory_gb = gpu.get("free_memory_gb", 8)

                if memory_gb >= 12:
                    return base_batch
                elif memory_gb >= 8:
                    return base_batch // 2
                else:
                    return max(base_batch // 4, 1)

            return base_batch

    def validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """驗證GPU配置"""
        if not config.get("use_multi_gpu", False):
            return True, "單GPU配置有效"

        device_ids = config.get("device_ids", [])

        if len(device_ids) < 2:
            return False, "多GPU模式需要至少2個GPU"

        for device_id in device_ids:
            if device_id >= self.gpu_count:
                return False, f"GPU {device_id} 不存在"

            if not self.gpu_info[device_id].get("available", False):
                return False, f"GPU {device_id} 不可用"

        return True, "多GPU配置有效"

    def save_gpu_report(self, filepath: Path):
        """保存GPU報告"""
        from datetime import datetime

        report = {
            "timestamp": datetime.now().isoformat(),
            "cuda_available": self.cuda_available,
            "gpu_count": self.gpu_count,
            "gpu_info": self.gpu_info,
            "nvidia_smi": self.get_nvidia_smi_info(),
            "optimal_config": self.get_optimal_device_setup(),
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


# 全域GPU管理器實例
_gpu_manager: Optional[GPUManager] = None


def get_gpu_manager() -> GPUManager:
    """獲取GPU管理器實例"""
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = GPUManager()
    return _gpu_manager
