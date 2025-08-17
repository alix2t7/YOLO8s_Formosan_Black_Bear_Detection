"""
完整的 YOLOv8s 熊類檢測訓練 Pipeline
整合環境建立/環境管理/超參搜索/正式訓練/訓練過程及結果保存

使用方式:
    python main.py --mode full                    # 完整流程
    python main.py --mode setup                   # 僅環境設置
    python main.py --mode optimize               # 僅超參優化
    python main.py --mode train                   # 僅訓練
    python main.py --mode validate               # 僅數據驗證
"""

import argparse
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utils.logger import YOLOLogger
from src.utils.file_manager import FileManager
from src.environment.setup import EnvironmentSetup
from src.environment.manager import EnvironmentManager
from src.data.loader import DataLoader
from src.data.validator import DataValidator
from src.optimization.optuna_optimizer import OptunaOptimizer
from src.training.trainer import YOLOv8sTrainer

class YOLOv8sPipeline:
    """YOLOv8s 完整訓練 Pipeline"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.logger = YOLOLogger()
        self.file_manager = FileManager()
        
        # 創建時間戳
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 加載配置
        self.base_config = self._load_config("base_config.yaml")
        self.training_config = self._load_config("training_config.yaml")
        self.optuna_config = self._load_config("optuna_config.yaml")
        
        # 初始化組件
        self.env_setup = None
        self.env_manager = None
        self.data_loader = None
        self.data_validator = None
        self.optimizer = None
        self.trainer = None
        
        # 結果目錄
        self.results_dir = os.path.join("results", f"pipeline_{self.timestamp}")
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.logger.info(f"🚀 YOLOv8s Pipeline 初始化完成")
        self.logger.info(f"📁 結果目錄: {self.results_dir}")
    
    def _load_config(self, config_name: str) -> Dict[str, Any]:
        """加載配置文件"""
        config_path = os.path.join(self.config_dir, config_name)
        if os.path.exists(config_path):
            return self.file_manager.load_config(config_path)
        else:
            self.logger.error(f"配置文件不存在: {config_path}")
            return {}
    
    def setup_environment(self) -> bool:
        """環境設置"""
        self.logger.info("🔧 開始環境設置...")
        
        try:
            # 初始化環境設置器
            self.env_setup = EnvironmentSetup()
            
            # 檢測平台
            platform_type = self.env_setup.platform_type  # 直接訪問屬性
            self.logger.info(f"📊 平台檢測: {platform_type}")
            
            # 安裝依賴 - 需要提供套件列表
            required_packages = [
                'torch', 'torchvision', 'ultralytics', 'optuna', 
                'numpy', 'opencv-python', 'Pillow', 'PyYAML', 
                'matplotlib', 'tqdm', 'psutil'
            ]
            install_results = self.env_setup.install_packages(required_packages)
            failed_packages = [pkg for pkg, success in install_results.items() if not success]
            if failed_packages:
                self.logger.warning(f"部分套件安裝失敗: {failed_packages}")
            
            # 設置 GPU
            cuda_info = self.env_setup.setup_cuda_environment()
            if not cuda_info.get('available', False):
                self.logger.warning("GPU 設置可能有問題，將使用 CPU")
            
            # 初始化環境管理器
            self.env_manager = EnvironmentManager()
            
            # 驗證環境
            validation_result = self.env_setup.validate_environment()
            if not validation_result.get('system_compatible', False) or not validation_result.get('python_compatible', False):
                self.logger.error("環境驗證失敗")
                for issue in validation_result.get('issues', []):
                    self.logger.error(f"  ❌ {issue}")
                return False
            
            # 記錄警告
            if validation_result.get('issues'):
                for issue in validation_result.get('issues', []):
                    self.logger.warning(f"  ⚠️  {issue}")
            
            self.logger.info("✅ 環境設置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"環境設置失敗: {str(e)}")
            return False
    
    def validate_data(self) -> bool:
        """數據驗證"""
        self.logger.info("🔍 開始數據驗證...")
        
        try:
            # 初始化數據組件
            self.data_loader = DataLoader(self.base_config)
            self.data_validator = DataValidator(self.base_config)
            
            # 檢查數據集設置
            if not self.data_loader.setup_dataset():
                self.logger.error("數據集設置失敗")
                return False
            
            # 完整數據驗證
            dataset_path = self.base_config.get('dataset', {}).get('path', '')
            validation_results = self.data_validator.validate_complete_dataset(dataset_path)
            
            # 保存驗證報告
            report_path = os.path.join(self.results_dir, "data_validation_report.json")
            self.data_validator.save_validation_report(validation_results, report_path)
            
            # 檢查驗證結果
            if not validation_results['is_valid']:
                self.logger.error("數據驗證失敗")
                for error in validation_results['errors']:
                    self.logger.error(f"  ❌ {error}")
                return False
            
            # 顯示警告
            for warning in validation_results['warnings']:
                self.logger.warning(f"  ⚠️  {warning}")
            
            # 顯示建議
            for recommendation in validation_results['recommendations']:
                self.logger.info(f"  💡 {recommendation}")
            
            # 顯示統計信息
            stats = validation_results['statistics']
            image_counts = stats.get('image_counts', {})
            self.logger.info(f"📊 訓練圖像: {image_counts.get('train', 0)}")
            self.logger.info(f"📊 驗證圖像: {image_counts.get('val', 0)}")
            
            self.logger.info("✅ 數據驗證完成")
            return True
            
        except Exception as e:
            self.logger.error(f"數據驗證失敗: {str(e)}")
            return False
    
    def optimize_hyperparameters(self) -> Optional[Dict[str, Any]]:
        """超參數優化"""
        self.logger.info("🔬 開始超參數優化...")
        
        try:
            # 初始化優化器
            self.optimizer = OptunaOptimizer(
                config_path=os.path.join(self.config_dir, "optuna_config.yaml")
            )
            # 設置 logger 
            self.optimizer.logger = self.logger
            
            # 執行優化
            n_trials = self.optuna_config.get('n_trials', 50)
            optimization_results = self.optimizer.optimize(n_trials=n_trials)
            
            # 獲取最佳參數
            best_params = self.optimizer.get_best_parameters()
            
            # 保存優化結果
            self.file_manager.save_config(
                optimization_results, 
                os.path.join(self.results_dir, "optimization_results.yaml")
            )
            
            self.logger.info("✅ 超參數優化完成")
            self.logger.info(f"🏆 最佳參數: {best_params}")
            
            return best_params
            
        except Exception as e:
            self.logger.error(f"超參數優化失敗: {str(e)}")
            return None
    
    def train_model(self, use_best_params: bool = True) -> bool:
        """訓練模型"""
        self.logger.info("🎯 開始模型訓練...")
        
        try:
            # 初始化訓練器
            self.trainer = YOLOv8sTrainer(
                config=self.training_config
            )
            
            # 設置訓練環境
            if not self.trainer.setup_environment():
                self.logger.error("訓練環境設置失敗")
                return False
            
            # 加載最佳參數（如果有）
            if use_best_params:
                best_params = self.trainer.load_best_params()
                if best_params:
                    self.logger.info("📥 使用優化後的最佳參數")
                else:
                    self.logger.info("📋 使用默認訓練參數")
            
            # 執行完整訓練
            training_results = self.trainer.run_complete_training()
            
            if training_results:
                # 保存訓練結果
                results_path = os.path.join(self.results_dir, "training_results.yaml")
                self.file_manager.save_config(training_results, results_path)
                
                self.logger.info("✅ 模型訓練完成")
                self.logger.info(f"🎯 最終性能: {training_results.get('final_metrics', {})}")
                
                return True
            else:
                self.logger.error("訓練失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"模型訓練失敗: {str(e)}")
            return False
    
    def run_full_pipeline(self) -> bool:
        """執行完整流程"""
        self.logger.info("🌟 開始完整 YOLOv8s 訓練流程")
        start_time = time.time()
        
        try:
            # 1. 環境設置
            if not self.setup_environment():
                return False
            
            # 2. 數據驗證
            if not self.validate_data():
                return False
            
            # 3. 超參數優化
            best_params = self.optimize_hyperparameters()
            
            # 4. 模型訓練
            if not self.train_model(use_best_params=best_params is not None):
                return False
            
            # 5. 生成總結報告
            self._generate_final_report(start_time)
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"🎉 完整流程執行成功！總用時: {elapsed_time/3600:.2f} 小時")
            
            return True
            
        except Exception as e:
            self.logger.error(f"完整流程執行失敗: {str(e)}")
            return False
    
    def _generate_final_report(self, start_time: float) -> None:
        """生成最終報告"""
        try:
            elapsed_time = time.time() - start_time
            
            report = {
                'pipeline_info': {
                    'timestamp': self.timestamp,
                    'total_time_hours': elapsed_time / 3600,
                    'results_directory': self.results_dir
                },
                'configuration': {
                    'base_config': self.base_config,
                    'training_config': self.training_config,
                    'optuna_config': self.optuna_config
                },
                'execution_summary': {
                    'environment_setup': '✅ 完成',
                    'data_validation': '✅ 完成',
                    'hyperparameter_optimization': '✅ 完成',
                    'model_training': '✅ 完成'
                }
            }
            
            # 保存報告
            report_path = os.path.join(self.results_dir, "pipeline_report.yaml")
            self.file_manager.save_config(report, report_path)
            
            self.logger.info(f"📋 最終報告已保存: {report_path}")
            
        except Exception as e:
            self.logger.error(f"生成最終報告失敗: {str(e)}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="YOLOv8s 熊類檢測訓練 Pipeline")
    parser.add_argument(
        '--mode', 
        choices=['full', 'setup', 'validate', 'optimize', 'train'],
        default='full',
        help='執行模式'
    )
    parser.add_argument(
        '--config-dir',
        default='config',
        help='配置文件目錄'
    )
    
    args = parser.parse_args()
    
    # 初始化 Pipeline
    pipeline = YOLOv8sPipeline(config_dir=args.config_dir)
    
    try:
        if args.mode == 'full':
            success = pipeline.run_full_pipeline()
        elif args.mode == 'setup':
            success = pipeline.setup_environment()
        elif args.mode == 'validate':
            success = pipeline.validate_data()
        elif args.mode == 'optimize':
            result = pipeline.optimize_hyperparameters()
            success = result is not None
        elif args.mode == 'train':
            success = pipeline.train_model()
        else:
            pipeline.logger.error(f"未知模式: {args.mode}")
            success = False
        
        if success:
            pipeline.logger.info("🎉 執行成功完成！")
            sys.exit(0)
        else:
            pipeline.logger.error("❌ 執行失敗")
            sys.exit(1)
            
    except KeyboardInterrupt:
        pipeline.logger.warning("⚠️  執行被用戶中斷")
        sys.exit(1)
    except Exception as e:
        pipeline.logger.error(f"執行過程中發生錯誤: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
