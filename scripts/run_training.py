"""
訓練腳本
獨立的模型訓練工具
"""

import sys
import os
import argparse

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.training.trainer import YOLOv8sTrainer
from src.utils.logger import YOLOLogger
from src.utils.file_manager import FileManager

def main():
    """訓練主函數"""
    parser = argparse.ArgumentParser(description="YOLOv8s 模型訓練")
    parser.add_argument(
        '--config', 
        default='config/training_config.yaml', 
        help='訓練配置文件路徑'
    )
    parser.add_argument(
        '--use-best-params', 
        action='store_true', 
        help='使用優化後的最佳參數'
    )
    parser.add_argument(
        '--resume', 
        default=None, 
        help='恢復訓練的檢查點路徑'
    )
    
    args = parser.parse_args()
    
    logger = YOLOLogger()
    file_manager = FileManager()
    
    logger.info("🎯 開始模型訓練...")
    
    try:
        # 加載訓練配置
        config = file_manager.load_config(args.config)
        
        # 初始化訓練器
        trainer = YOLOv8sTrainer(config=config, logger=logger)
        
        # 設置訓練環境
        if not trainer.setup_environment():
            logger.error("❌ 訓練環境設置失敗")
            return False
        
        # 加載最佳參數（如果指定）
        if args.use_best_params:
            best_params = trainer.load_best_params()
            if best_params:
                logger.info("📥 使用優化後的最佳參數")
            else:
                logger.warning("⚠️ 未找到最佳參數，使用默認配置")
        
        # 執行訓練
        results = trainer.run_complete_training()
        
        if results:
            logger.info("🎉 訓練完成！")
            logger.info(f"📊 最終性能: {results.get('final_metrics', {})}")
            return True
        else:
            logger.error("❌ 訓練失敗")
            return False
            
    except Exception as e:
        logger.error(f"❌ 訓練過程出錯: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
