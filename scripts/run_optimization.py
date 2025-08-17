"""
超參數優化腳本
獨立的 Optuna 超參數搜索工具
"""

import sys
import os
import argparse

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.optimization.optuna_optimizer import OptunaOptimizer
from src.utils.logger import YOLOLogger

def main():
    """超參數優化主函數"""
    parser = argparse.ArgumentParser(description="YOLOv8s 超參數優化")
    parser.add_argument(
        '--trials', 
        type=int, 
        default=50, 
        help='優化試驗次數'
    )
    parser.add_argument(
        '--config', 
        default='config/optuna_config.yaml', 
        help='優化配置文件路徑'
    )
    
    args = parser.parse_args()
    
    logger = YOLOLogger()
    logger.info(f"🔬 開始超參數優化，試驗次數: {args.trials}")
    
    try:
        # 初始化優化器
        optimizer = OptunaOptimizer(
            config_path=args.config,
            logger=logger
        )
        
        # 執行優化
        results = optimizer.optimize(n_trials=args.trials)
        
        if results:
            best_params = optimizer.get_best_parameters()
            logger.info(f"🏆 優化完成！最佳參數: {best_params}")
            return True
        else:
            logger.error("❌ 優化失敗")
            return False
            
    except Exception as e:
        logger.error(f"❌ 優化過程出錯: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
