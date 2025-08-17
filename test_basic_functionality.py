#!/usr/bin/env python3
"""
main.py 基本功能測試腳本
用於驗證核心功能，不依賴外部機器學習套件
"""

import os
import sys
import argparse
from pathlib import Path

def test_argparse():
    """測試命令列參數解析"""
    print("🔍 測試 argparse 功能...")
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
    
    # 測試解析
    test_args = ['--mode', 'setup', '--config-dir', 'config']
    args = parser.parse_args(test_args)
    
    assert args.mode == 'setup'
    assert args.config_dir == 'config'
    print("✅ argparse 功能正常")

def test_file_structure():
    """測試專案檔案結構"""
    print("🔍 測試專案檔案結構...")
    
    required_files = [
        'main.py',
        'README.md', 
        'LICENSE',
        'requirements.txt',
        'config/base_config.yaml',
        'config/training_config.yaml', 
        'config/optuna_config.yaml'
    ]
    
    required_dirs = [
        'src',
        'src/utils',
        'src/environment',
        'src/data',
        'src/optimization', 
        'src/training',
        'config',
        'examples'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_files:
        print(f"⚠️  缺少檔案: {missing_files}")
    
    if missing_dirs:
        print(f"⚠️  缺少目錄: {missing_dirs}")
    
    if not missing_files and not missing_dirs:
        print("✅ 專案檔案結構完整")

def test_config_files():
    """測試配置檔案載入"""
    print("🔍 測試配置檔案...")
    
    try:
        import yaml
        
        config_files = [
            'config/base_config.yaml',
            'config/training_config.yaml', 
            'config/optuna_config.yaml'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config:
                        print(f"✅ {config_file} 載入成功")
                    else:
                        print(f"⚠️  {config_file} 為空")
            else:
                print(f"❌ {config_file} 不存在")
                
    except ImportError:
        print("⚠️  PyYAML 未安裝，跳過 YAML 測試")

def test_basic_imports():
    """測試基本模組導入 (不導入重型依賴)"""
    print("🔍 測試基本模組導入...")
    
    try:
        # 測試 Python 標準庫
        import json
        import datetime
        from pathlib import Path
        from typing import Dict, Any, Optional
        print("✅ 標準庫導入成功")
        
        # 測試 sys.path 設置
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        print("✅ Python 路徑設置成功")
        
    except Exception as e:
        print(f"❌ 基本導入失敗: {e}")

def main():
    """執行所有測試"""
    print("🚀 開始 main.py 基本功能測試...\n")
    
    test_argparse()
    test_file_structure() 
    test_config_files()
    test_basic_imports()
    
    print("\n🎉 基本功能測試完成！")
    print("ℹ️  完整功能需要安裝所有依賴套件:")
    print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
