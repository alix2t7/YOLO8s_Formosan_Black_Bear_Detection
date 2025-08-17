"""
環境設置腳本
獨立的環境設置工具
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.environment.setup import EnvironmentSetup
from src.utils.logger import YOLOLogger

def main():
    """環境設置主函數"""
    logger = YOLOLogger()
    logger.info("🔧 開始環境設置...")
    
    try:
        # 初始化環境設置器
        env_setup = EnvironmentSetup()
        
        # 檢測平台
        platform_info = env_setup.detect_platform()
        logger.info(f"📊 檢測到平台: {platform_info['platform']}")
        
        # 安裝依賴
        logger.info("📦 安裝依賴套件...")
        if not env_setup.install_requirements():
            logger.error("❌ 依賴安裝失敗")
            return False
        
        # 設置 CUDA
        logger.info("🚀 設置 GPU 環境...")
        if not env_setup.setup_cuda():
            logger.warning("⚠️ GPU 設置可能有問題，將使用 CPU")
        
        # 驗證環境
        logger.info("✅ 驗證環境...")
        if not env_setup.validate_environment():
            logger.error("❌ 環境驗證失敗")
            return False
        
        logger.info("🎉 環境設置完成！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 環境設置失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
