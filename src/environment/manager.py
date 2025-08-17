"""
環境管理器
提供環境狀態監控和管理功能
"""

import os
import psutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import threading
import json

class EnvironmentManager:
    """環境管理器 - 監控和管理訓練環境"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 30  # 秒
        self.monitor_data = []
        self.callbacks = []
        
        # 資源閾值
        self.thresholds = {
            'cpu_percent': 95.0,
            'memory_percent': 90.0,
            'disk_percent': 95.0,
            'gpu_memory_percent': 95.0
        }
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """添加監控回調函數"""
        self.callbacks.append(callback)
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'cpu': self._get_cpu_status(),
            'memory': self._get_memory_status(),
            'disk': self._get_disk_status(),
            'gpu': self._get_gpu_status(),
            'processes': self._get_process_status()
        }
        
        return status
    
    def _get_cpu_status(self) -> Dict[str, Any]:
        """獲取CPU狀態"""
        try:
            return {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_memory_status(self) -> Dict[str, Any]:
        """獲取記憶體狀態"""
        try:
            vm = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'virtual': {
                    'total_gb': vm.total / 1024**3,
                    'available_gb': vm.available / 1024**3,
                    'used_gb': vm.used / 1024**3,
                    'percent': vm.percent
                },
                'swap': {
                    'total_gb': swap.total / 1024**3,
                    'used_gb': swap.used / 1024**3,
                    'percent': swap.percent
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_status(self) -> Dict[str, Any]:
        """獲取磁盤狀態"""
        try:
            usage = psutil.disk_usage('/')
            io = psutil.disk_io_counters()
            
            return {
                'usage': {
                    'total_gb': usage.total / 1024**3,
                    'used_gb': usage.used / 1024**3,
                    'free_gb': usage.free / 1024**3,
                    'percent': (usage.used / usage.total) * 100
                },
                'io': {
                    'read_bytes': io.read_bytes if io else 0,
                    'write_bytes': io.write_bytes if io else 0,
                    'read_count': io.read_count if io else 0,
                    'write_count': io.write_count if io else 0
                } if io else None
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_gpu_status(self) -> Dict[str, Any]:
        """獲取GPU狀態"""
        try:
            import torch
            
            if not torch.cuda.is_available():
                return {'available': False}
            
            gpus = []
            for i in range(torch.cuda.device_count()):
                torch.cuda.set_device(i)
                
                # 獲取GPU屬性
                props = torch.cuda.get_device_properties(i)
                allocated = torch.cuda.memory_allocated(i)
                reserved = torch.cuda.memory_reserved(i)
                total = props.total_memory
                
                gpu_info = {
                    'id': i,
                    'name': props.name,
                    'memory': {
                        'total_gb': total / 1024**3,
                        'allocated_gb': allocated / 1024**3,
                        'reserved_gb': reserved / 1024**3,
                        'free_gb': (total - allocated) / 1024**3,
                        'utilization_percent': (allocated / total) * 100
                    }
                }
                
                gpus.append(gpu_info)
            
            return {
                'available': True,
                'count': len(gpus),
                'gpus': gpus
            }
            
        except ImportError:
            return {'available': False, 'error': 'PyTorch not available'}
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def _get_process_status(self) -> Dict[str, Any]:
        """獲取進程狀態"""
        try:
            current_process = psutil.Process()
            
            return {
                'pid': current_process.pid,
                'cpu_percent': current_process.cpu_percent(),
                'memory_percent': current_process.memory_percent(),
                'memory_info': current_process.memory_info()._asdict(),
                'num_threads': current_process.num_threads(),
                'create_time': current_process.create_time()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_resource_limits(self, status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """檢查資源限制"""
        warnings = []
        
        # CPU 檢查
        cpu_percent = status.get('cpu', {}).get('percent', 0)
        if cpu_percent > self.thresholds['cpu_percent']:
            warnings.append({
                'type': 'cpu_high',
                'message': f'CPU使用率過高: {cpu_percent:.1f}%',
                'value': cpu_percent,
                'threshold': self.thresholds['cpu_percent']
            })
        
        # 記憶體檢查
        memory_percent = status.get('memory', {}).get('virtual', {}).get('percent', 0)
        if memory_percent > self.thresholds['memory_percent']:
            warnings.append({
                'type': 'memory_high',
                'message': f'記憶體使用率過高: {memory_percent:.1f}%',
                'value': memory_percent,
                'threshold': self.thresholds['memory_percent']
            })
        
        # 磁盤檢查
        disk_percent = status.get('disk', {}).get('usage', {}).get('percent', 0)
        if disk_percent > self.thresholds['disk_percent']:
            warnings.append({
                'type': 'disk_high',
                'message': f'磁盤使用率過高: {disk_percent:.1f}%',
                'value': disk_percent,
                'threshold': self.thresholds['disk_percent']
            })
        
        # GPU 檢查
        gpu_status = status.get('gpu', {})
        if gpu_status.get('available', False):
            for gpu in gpu_status.get('gpus', []):
                gpu_memory_percent = gpu.get('memory', {}).get('utilization_percent', 0)
                if gpu_memory_percent > self.thresholds['gpu_memory_percent']:
                    warnings.append({
                        'type': 'gpu_memory_high',
                        'message': f'GPU {gpu["id"]} 記憶體使用率過高: {gpu_memory_percent:.1f}%',
                        'value': gpu_memory_percent,
                        'threshold': self.thresholds['gpu_memory_percent'],
                        'gpu_id': gpu['id']
                    })
        
        return warnings
    
    def start_monitoring(self, interval: int = 30):
        """開始監控"""
        if self.monitoring:
            print("⚠️  監控已在運行中")
            return
        
        self.monitor_interval = interval
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    status = self.get_system_status()
                    warnings = self.check_resource_limits(status)
                    
                    # 記錄數據
                    monitor_entry = {
                        'status': status,
                        'warnings': warnings
                    }
                    self.monitor_data.append(monitor_entry)
                    
                    # 限制數據量
                    if len(self.monitor_data) > 1000:
                        self.monitor_data = self.monitor_data[-500:]
                    
                    # 調用回調函數
                    for callback in self.callbacks:
                        try:
                            callback(monitor_entry)
                        except Exception as e:
                            print(f"⚠️  監控回調錯誤: {e}")
                    
                    # 如果有警告，打印出來
                    if warnings:
                        for warning in warnings:
                            print(f"⚠️  {warning['message']}")
                    
                    time.sleep(self.monitor_interval)
                    
                except Exception as e:
                    print(f"❌ 監控錯誤: {e}")
                    time.sleep(self.monitor_interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"✅ 系統監控已啟動 (間隔: {interval}秒)")
    
    def stop_monitoring(self):
        """停止監控"""
        if not self.monitoring:
            print("⚠️  監控未在運行")
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("✅ 系統監控已停止")
    
    def get_monitoring_summary(self, hours: int = 1) -> Dict[str, Any]:
        """獲取監控摘要"""
        if not self.monitor_data:
            return {'error': '無監控數據'}
        
        # 計算時間範圍
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 篩選數據
        recent_data = []
        for entry in self.monitor_data:
            timestamp_str = entry['status']['timestamp']
            timestamp = datetime.fromisoformat(timestamp_str)
            if timestamp >= cutoff_time:
                recent_data.append(entry)
        
        if not recent_data:
            return {'error': f'過去{hours}小時內無監控數據'}
        
        # 計算統計信息
        cpu_values = []
        memory_values = []
        gpu_memory_values = []
        warning_counts = {}
        
        for entry in recent_data:
            status = entry['status']
            
            # CPU
            cpu_percent = status.get('cpu', {}).get('percent')
            if cpu_percent is not None:
                cpu_values.append(cpu_percent)
            
            # 記憶體
            memory_percent = status.get('memory', {}).get('virtual', {}).get('percent')
            if memory_percent is not None:
                memory_values.append(memory_percent)
            
            # GPU
            gpu_status = status.get('gpu', {})
            if gpu_status.get('available', False):
                for gpu in gpu_status.get('gpus', []):
                    gpu_memory_percent = gpu.get('memory', {}).get('utilization_percent')
                    if gpu_memory_percent is not None:
                        gpu_memory_values.append(gpu_memory_percent)
            
            # 警告統計
            for warning in entry['warnings']:
                warning_type = warning['type']
                warning_counts[warning_type] = warning_counts.get(warning_type, 0) + 1
        
        summary = {
            'time_range_hours': hours,
            'data_points': len(recent_data),
            'cpu': self._calculate_stats(cpu_values),
            'memory': self._calculate_stats(memory_values),
            'gpu_memory': self._calculate_stats(gpu_memory_values),
            'warnings': warning_counts
        }
        
        return summary
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """計算統計信息"""
        if not values:
            return {}
        
        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }
    
    def save_monitoring_data(self, filepath: Path):
        """保存監控數據"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'saved_at': datetime.now().isoformat(),
            'thresholds': self.thresholds,
            'monitor_data': self.monitor_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 監控數據已保存: {filepath}")
    
    def clear_monitoring_data(self):
        """清除監控數據"""
        self.monitor_data.clear()
        print("✅ 監控數據已清除")
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """獲取平台限制"""
        limits = {
            'detected_platform': 'local',
            'time_limit_hours': None,
            'memory_limit_gb': None,
            'disk_limit_gb': None
        }
        
        # Kaggle 檢測
        if os.path.exists('/kaggle'):
            limits.update({
                'detected_platform': 'kaggle',
                'time_limit_hours': 12,  # Kaggle notebook 限制
                'memory_limit_gb': 16,   # 一般配置
                'disk_limit_gb': 20      # 工作目錄限制
            })
        
        # Colab 檢測
        try:
            import google.colab
            limits.update({
                'detected_platform': 'colab',
                'time_limit_hours': 12,  # Colab 空閒斷線
                'memory_limit_gb': 12,   # 一般配置
                'disk_limit_gb': 100     # 較大磁盤空間
            })
        except ImportError:
            pass
        
        return limits
    
    def optimize_for_platform(self) -> Dict[str, Any]:
        """針對平台優化設置"""
        limits = self.get_platform_limits()
        platform = limits['detected_platform']
        
        optimizations = {
            'platform': platform,
            'applied_optimizations': []
        }
        
        if platform == 'kaggle':
            # Kaggle 優化
            optimizations['applied_optimizations'].extend([
                '啟用記憶體監控',
                '設置時間限制為10小時',
                '啟用積極快取清理',
                '優化批次大小'
            ])
            
            # 調整閾值
            self.thresholds.update({
                'memory_percent': 85.0,  # Kaggle記憶體較緊張
                'disk_percent': 90.0     # 磁盤空間有限
            })
            
        elif platform == 'colab':
            # Colab 優化
            optimizations['applied_optimizations'].extend([
                '啟用斷線保護',
                '設置自動保存',
                '優化GPU記憶體使用'
            ])
            
            # 調整閾值
            self.thresholds.update({
                'gpu_memory_percent': 90.0  # Colab GPU共享
            })
        
        print(f"✅ 已針對 {platform} 平台進行優化")
        for opt in optimizations['applied_optimizations']:
            print(f"  - {opt}")
        
        return optimizations

# 全域環境管理器實例
_environment_manager: Optional[EnvironmentManager] = None

def get_environment_manager() -> EnvironmentManager:
    """獲取環境管理器實例"""
    global _environment_manager
    if _environment_manager is None:
        _environment_manager = EnvironmentManager()
    return _environment_manager
