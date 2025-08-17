"""
環境設置模組
提供環境檢測、安裝和配置功能
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import importlib.util

class EnvironmentSetup:
    """環境設置器"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.python_info = self._get_python_info()
        self.platform_type = self._detect_platform()
        
    def _get_system_info(self) -> Dict[str, Any]:
        """獲取系統信息"""
        try:
            import psutil
            
            return {
                'os': platform.system(),
                'os_version': platform.release(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'cpu_count': os.cpu_count(),
                'total_memory_gb': psutil.virtual_memory().total / 1024**3,
                'available_memory_gb': psutil.virtual_memory().available / 1024**3,
                'disk_usage': {
                    'total_gb': psutil.disk_usage('/').total / 1024**3,
                    'free_gb': psutil.disk_usage('/').free / 1024**3
                }
            }
        except ImportError:
            return {
                'os': platform.system(),
                'os_version': platform.release(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'cpu_count': os.cpu_count()
            }
    
    def _get_python_info(self) -> Dict[str, Any]:
        """獲取Python信息"""
        return {
            'version': platform.python_version(),
            'implementation': platform.python_implementation(),
            'executable': sys.executable,
            'prefix': sys.prefix,
            'path': sys.path[:3]  # 只取前3個路徑
        }
    
    def _detect_platform(self) -> str:
        """檢測運行平台 - 改進版本"""
        # Kaggle 檢測 (多種方式)
        kaggle_indicators = [
            os.path.exists('/kaggle'),
            os.environ.get('KAGGLE_KERNEL_RUN_TYPE') is not None,
            os.environ.get('KAGGLE_URL_BASE') is not None,
            '/kaggle' in os.getcwd()
        ]
        if any(kaggle_indicators):
            return 'kaggle'
        
        # Google Colab 檢測 (多種方式)
        colab_indicators = [
            'COLAB_GPU' in os.environ,
            'COLAB_TPU_ADDR' in os.environ,
            os.path.exists('/content'),
            '/content' in os.getcwd()
        ]
        
        # 嘗試導入 google.colab
        try:
            import google.colab
            colab_indicators.append(True)
        except ImportError:
            pass
        
        if any(colab_indicators):
            return 'colab'
        
        # Jupyter 檢測 (改進版本)
        jupyter_indicators = []
        try:
            from IPython.core.getipython import get_ipython
            ipython = get_ipython()
            if ipython is not None:
                jupyter_indicators.append(True)
                # 檢查是否在 notebook 環境
                if hasattr(ipython, 'kernel'):
                    jupyter_indicators.append(True)
        except ImportError:
            pass
        
        # 檢查 Jupyter 環境變數
        if os.environ.get('JPY_PARENT_PID') is not None:
            jupyter_indicators.append(True)
        
        if any(jupyter_indicators):
            return 'jupyter'
        
        # Docker 檢測
        docker_indicators = [
            os.path.exists('/.dockerenv'),
            os.environ.get('DOCKER_CONTAINER') is not None
        ]
        
        # 安全檢查 /proc/1/cgroup
        try:
            if os.path.exists('/proc/1/cgroup'):
                with open('/proc/1/cgroup', 'r') as f:
                    content = f.read()
                    if 'docker' in content:
                        docker_indicators.append(True)
        except (IOError, PermissionError):
            pass
        
        if any(docker_indicators):
            return 'docker'
        
        # 本地環境
        return 'local'
    
    def check_package_availability(self, packages: List[str]) -> Dict[str, Dict[str, Any]]:
        """檢查套件可用性"""
        results = {}
        
        for package in packages:
            try:
                spec = importlib.util.find_spec(package)
                if spec is not None:
                    module = importlib.import_module(package)
                    version = getattr(module, '__version__', 'unknown')
                    results[package] = {
                        'available': True,
                        'version': version,
                        'location': spec.origin
                    }
                else:
                    results[package] = {'available': False}
            except Exception as e:
                results[package] = {
                    'available': False,
                    'error': str(e)
                }
        
        return results
    
    def install_packages(self, packages: List[str], 
                        upgrade: bool = False,
                        quiet: bool = True) -> Dict[str, bool]:
        """安裝套件"""
        results = {}
        
        for package in packages:
            try:
                cmd = [sys.executable, '-m', 'pip', 'install']
                
                if upgrade:
                    cmd.append('--upgrade')
                
                if quiet:
                    cmd.extend(['--quiet', '--no-warn-script-location'])
                
                cmd.append(package)
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                results[package] = result.returncode == 0
                
                if result.returncode != 0:
                    print(f"❌ 安裝 {package} 失敗: {result.stderr}")
                else:
                    print(f"✅ 成功安裝 {package}")
                    
            except Exception as e:
                print(f"❌ 安裝 {package} 時發生錯誤: {e}")
                results[package] = False
        
        return results
    
    def setup_cuda_environment(self) -> Dict[str, Any]:
        """設置CUDA環境"""
        cuda_info: Dict[str, Any] = {'available': False}
        
        try:
            import torch
            
            # 修正類型註解問題
            cuda_info['available'] = torch.cuda.is_available()
            # 簡化版本檢測 - 避免訪問不存在的屬性
            if torch.cuda.is_available():
                cuda_info['version'] = "available"  # 簡化為可用狀態
            else:
                cuda_info['version'] = None
            cuda_info['device_count'] = torch.cuda.device_count() if torch.cuda.is_available() else 0
            
            if torch.cuda.is_available():
                devices = []
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    devices.append({
                        'id': i,
                        'name': props.name,
                        'memory_gb': props.total_memory / 1024**3,
                        'compute_capability': f"{props.major}.{props.minor}"
                    })
                cuda_info['devices'] = devices
                
        except ImportError:
            cuda_info['error'] = 'PyTorch 未安裝'
        
        return cuda_info
    
    def configure_warnings(self):
        """配置警告設置"""
        import warnings
        
        # 抑制常見警告
        warnings.filterwarnings("ignore", ".*iCCP.*", UserWarning)
        warnings.filterwarnings("ignore", ".*known incorrect sRGB profile.*", UserWarning)
        warnings.filterwarnings("ignore", ".*Corrupt EXIF data.*", UserWarning)
        
        # 設置環境變數
        os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'
        os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
        
        # PIL 設置
        try:
            from PIL import Image
            Image.MAX_IMAGE_PIXELS = None
        except ImportError:
            pass
        
        print("✅ 警告抑制已配置")
    
    def setup_directories(self, base_dir: Path) -> Dict[str, Path]:
        """設置項目目錄結構"""
        directories = {
            'base': base_dir,
            'config': base_dir / 'config',
            'data': base_dir / 'data', 
            'models': base_dir / 'models',
            'results': base_dir / 'results',
            'logs': base_dir / 'logs',
            'cache': base_dir / 'cache',
            'temp': base_dir / 'temp'
        }
        
        for name, path in directories.items():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 目錄已創建: {path}")
        
        return directories
    
    def create_data_yaml(self, config: Dict[str, Any]) -> Path:
        """創建數據集配置文件"""
        import yaml
        
        data_config = {
            'path': config.get('dataset_path', './data'),
            'train': config.get('train_path', 'images/train'),
            'val': config.get('val_path', 'images/val'),
            'test': config.get('test_path', 'images/val'),
            'nc': config.get('num_classes', 2),
            'names': config.get('class_names', ['kumay', 'not_kumay'])
        }
        
        data_yaml_path = Path(config.get('data_yaml_path', './data.yaml'))
        data_yaml_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(data_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data_config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ 數據配置文件已創建: {data_yaml_path}")
        return data_yaml_path
    
    def validate_environment(self) -> Dict[str, Any]:
        """驗證環境設置"""
        validation = {
            'system_compatible': True,
            'python_compatible': True,
            'packages_available': True,
            'cuda_available': False,
            'issues': []
        }
        
        # 檢查Python版本
        python_version = tuple(map(int, platform.python_version().split('.')))
        if python_version < (3, 8):
            validation['python_compatible'] = False
            validation['issues'].append(f"需要Python 3.8+，當前版本: {platform.python_version()}")
        
        # 檢查必要套件
        required_packages = ['torch', 'ultralytics', 'numpy', 'opencv-python', 'Pillow', 'PyYAML']
        package_status = self.check_package_availability(required_packages)
        
        missing_packages = [pkg for pkg, status in package_status.items() 
                          if not status.get('available', False)]
        
        if missing_packages:
            validation['packages_available'] = False
            validation['issues'].append(f"缺少套件: {', '.join(missing_packages)}")
        
        # 檢查CUDA
        cuda_info = self.setup_cuda_environment()
        validation['cuda_available'] = cuda_info.get('available', False)
        
        if not validation['cuda_available']:
            validation['issues'].append("CUDA 不可用，將使用CPU訓練")
        
        # 檢查磁盤空間
        if 'disk_usage' in self.system_info:
            free_gb = self.system_info['disk_usage']['free_gb']
            if free_gb < 10:
                validation['issues'].append(f"磁盤空間不足: {free_gb:.1f}GB 可用，建議至少50GB")
        
        return validation
    
    def print_environment_report(self):
        """打印環境報告"""
        print("=" * 60)
        print("🔍 環境檢測報告")
        print("=" * 60)
        
        # 系統信息
        print(f"📋 系統信息:")
        print(f"  操作系統: {self.system_info.get('os')} {self.system_info.get('os_version')}")
        print(f"  架構: {self.system_info.get('architecture')}")
        print(f"  CPU 核心: {self.system_info.get('cpu_count')}")
        
        if 'total_memory_gb' in self.system_info:
            print(f"  總記憶體: {self.system_info['total_memory_gb']:.1f} GB")
            print(f"  可用記憶體: {self.system_info['available_memory_gb']:.1f} GB")
        
        # Python 信息
        print(f"\n🐍 Python 信息:")
        print(f"  版本: {self.python_info['version']}")
        print(f"  實現: {self.python_info['implementation']}")
        print(f"  執行檔: {self.python_info['executable']}")
        
        # 平台信息
        print(f"\n🌐 平台類型: {self.platform_type}")
        
        # CUDA 信息
        cuda_info = self.setup_cuda_environment()
        print(f"\n🚀 CUDA 信息:")
        if cuda_info['available']:
            print(f"  狀態: ✅ 可用")
            print(f"  版本: {cuda_info.get('version', 'unknown')}")
            print(f"  設備數量: {cuda_info.get('device_count', 0)}")
            
            for device in cuda_info.get('devices', []):
                print(f"    GPU {device['id']}: {device['name']} "
                      f"({device['memory_gb']:.1f}GB, CC {device['compute_capability']})")
        else:
            print(f"  狀態: ❌ 不可用")
            if 'error' in cuda_info:
                print(f"  錯誤: {cuda_info['error']}")
        
        # 驗證結果
        validation = self.validate_environment()
        print(f"\n✅ 環境驗證:")
        print(f"  系統兼容: {'✅' if validation['system_compatible'] else '❌'}")
        print(f"  Python兼容: {'✅' if validation['python_compatible'] else '❌'}")
        print(f"  套件完整: {'✅' if validation['packages_available'] else '❌'}")
        print(f"  CUDA可用: {'✅' if validation['cuda_available'] else '❌'}")
        
        if validation['issues']:
            print(f"\n⚠️  發現問題:")
            for issue in validation['issues']:
                print(f"  - {issue}")
        
        print("=" * 60)

def setup_environment(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    設置完整環境
    
    Args:
        config: 環境配置
        
    Returns:
        設置結果
    """
    setup = EnvironmentSetup()
    
    print("🚀 開始環境設置...")
    
    # 打印環境報告
    setup.print_environment_report()
    
    # 配置警告
    setup.configure_warnings()
    
    # 安裝缺失套件
    if config.get('auto_install_packages', True):
        required_packages = config.get('required_packages', [
            'torch', 'torchvision', 'ultralytics', 'optuna', 
            'numpy', 'opencv-python', 'Pillow', 'PyYAML', 'matplotlib', 'tqdm'
        ])
        
        package_status = setup.check_package_availability(required_packages)
        missing_packages = [pkg for pkg, status in package_status.items() 
                          if not status.get('available', False)]
        
        if missing_packages:
            print(f"📦 安裝缺失套件: {missing_packages}")
            install_results = setup.install_packages(missing_packages)
            
            failed_installs = [pkg for pkg, success in install_results.items() if not success]
            if failed_installs:
                print(f"❌ 以下套件安裝失敗: {failed_installs}")
    
    # 設置目錄結構
    if 'base_directory' in config:
        base_dir = Path(config['base_directory'])
        directories = setup.setup_directories(base_dir)
        print(f"📁 項目目錄已設置: {base_dir}")
    
    # 創建數據配置
    if config.get('create_data_yaml', True):
        data_yaml_path = setup.create_data_yaml(config)
    
    # 最終驗證
    validation = setup.validate_environment()
    
    print("✅ 環境設置完成!")
    
    return {
        'setup': setup,
        'validation': validation,
        'platform': setup.platform_type,
        'cuda_available': validation['cuda_available']
    }
