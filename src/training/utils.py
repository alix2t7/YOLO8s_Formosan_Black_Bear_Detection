"""
訓練工具函數
"""

import yaml
import os
import json
import shutil
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

class TrainingUtils:
    """訓練工具類"""
    
    @staticmethod
    def create_timestamp() -> str:
        """創建時間戳"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def save_training_config(config: Dict[str, Any], save_path: str) -> None:
        """保存訓練配置"""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    @staticmethod
    def save_training_results(results: Dict[str, Any], save_path: str) -> None:
        """保存訓練結果"""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def backup_model(model_path: str, backup_dir: str, prefix: str = "backup") -> str:
        """備份模型"""
        timestamp = TrainingUtils.create_timestamp()
        backup_name = f"{prefix}_{timestamp}.pt"
        backup_path = os.path.join(backup_dir, backup_name)
        
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(model_path, backup_path)
        
        return backup_path
    
    @staticmethod
    def plot_training_metrics(metrics_history: List[Dict], save_path: str) -> None:
        """繪製訓練指標圖表"""
        if not metrics_history:
            return
        
        # 提取指標數據
        epochs = [entry['epoch'] for entry in metrics_history]
        metrics_data = {}
        
        for entry in metrics_history:
            for metric, value in entry['metrics'].items():
                if metric not in metrics_data:
                    metrics_data[metric] = []
                metrics_data[metric].append(value)
        
        # 創建圖表
        num_metrics = len(metrics_data)
        if num_metrics == 0:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        for i, (metric_name, values) in enumerate(metrics_data.items()):
            if i >= len(axes):
                break
            
            ax = axes[i]
            ax.plot(epochs, values, color=colors[i % len(colors)], linewidth=2, marker='o', markersize=4)
            ax.set_title(f'{metric_name}', fontsize=12, fontweight='bold')
            ax.set_xlabel('Epoch')
            ax.set_ylabel(metric_name)
            ax.grid(True, alpha=0.3)
        
        # 隱藏未使用的子圖
        for i in range(num_metrics, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    @staticmethod
    def calculate_training_stats(metrics_history: List[Dict]) -> Dict[str, Any]:
        """計算訓練統計"""
        if not metrics_history:
            return {}
        
        stats = {
            'total_epochs': len(metrics_history),
            'start_time': metrics_history[0].get('timestamp', ''),
            'end_time': metrics_history[-1].get('timestamp', ''),
            'metrics_summary': {}
        }
        
        # 計算每個指標的統計
        all_metrics = {}
        for entry in metrics_history:
            for metric, value in entry['metrics'].items():
                if metric not in all_metrics:
                    all_metrics[metric] = []
                all_metrics[metric].append(value)
        
        for metric, values in all_metrics.items():
            stats['metrics_summary'][metric] = {
                'final': values[-1],
                'best': max(values),
                'worst': min(values),
                'average': sum(values) / len(values),
                'improvement': values[-1] - values[0] if len(values) > 1 else 0
            }
        
        return stats
    
    @staticmethod
    def format_time_elapsed(start_time: float) -> str:
        """格式化耗時"""
        elapsed = time.time() - start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    @staticmethod
    def cleanup_old_checkpoints(checkpoint_dir: str, keep_last: int = 5) -> None:
        """清理舊的檢查點"""
        if not os.path.exists(checkpoint_dir):
            return
        
        # 獲取所有檢查點文件
        checkpoint_files = []
        for file in os.listdir(checkpoint_dir):
            if file.endswith('.pt'):
                file_path = os.path.join(checkpoint_dir, file)
                mtime = os.path.getmtime(file_path)
                checkpoint_files.append((file_path, mtime))
        
        # 按修改時間排序
        checkpoint_files.sort(key=lambda x: x[1], reverse=True)
        
        # 刪除舊文件
        for file_path, _ in checkpoint_files[keep_last:]:
            try:
                os.remove(file_path)
                print(f"🗑️  已清理舊檢查點: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"⚠️  清理檢查點失敗: {e}")
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """驗證配置文件"""
        errors = []
        
        # 檢查必需字段
        required_fields = ['model', 'data', 'epochs', 'batch_size']
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")
        
        # 檢查數值範圍
        if 'epochs' in config and (config['epochs'] <= 0 or config['epochs'] > 1000):
            errors.append("epochs 必須在 1-1000 之間")
        
        if 'batch_size' in config and (config['batch_size'] <= 0 or config['batch_size'] > 256):
            errors.append("batch_size 必須在 1-256 之間")
        
        if 'lr0' in config and (config['lr0'] <= 0 or config['lr0'] > 1):
            errors.append("lr0 必須在 0-1 之間")
        
        # 檢查文件路徑
        if 'data' in config and not os.path.exists(config['data']):
            errors.append(f"數據配置文件不存在: {config['data']}")
        
        return len(errors) == 0, errors

import time
