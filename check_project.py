"""
項目完整性檢查腳本
驗證所有必要文件和目錄是否存在
"""

import os
import sys
from pathlib import Path

def check_project_structure():
    """檢查項目結構完整性"""
    project_root = Path(__file__).parent
    
    # 必需的文件
    required_files = [
        "main.py",
        "setup.sh", 
        "requirements.txt",
        "README.md",
        "config/base_config.yaml",
        "config/training_config.yaml",
        "config/optuna_config.yaml",
        "scripts/setup_environment.py",
        "scripts/run_optimization.py",
        "scripts/run_training.py",
        "scripts/run_pipeline.py",
        "src/__init__.py",
        "src/utils/__init__.py",
        "src/utils/logger.py",
        "src/utils/gpu_manager.py", 
        "src/utils/file_manager.py",
        "src/environment/__init__.py",
        "src/environment/setup.py",
        "src/environment/manager.py",
        "src/data/__init__.py",
        "src/data/loader.py",
        "src/data/validator.py",
        "src/optimization/__init__.py",
        "src/optimization/optuna_optimizer.py",
        "src/optimization/search_strategies.py",
        "src/training/__init__.py",
        "src/training/trainer.py",
        "src/training/callbacks.py",
        "src/training/utils.py"
    ]
    
    # 必需的目錄
    required_dirs = [
        "config",
        "scripts", 
        "src",
        "src/utils",
        "src/environment",
        "src/data",
        "src/optimization", 
        "src/training",
        "results",
        "results/training",
        "results/optimization",
        "results/models",
        "logs",
        "checkpoints",
        "data"
    ]
    
    missing_files = []
    missing_dirs = []
    
    print("🔍 檢查項目結構完整性...")
    print("=" * 50)
    
    # 檢查文件
    print("\n📄 檢查必需文件:")
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    # 檢查目錄
    print("\n📁 檢查必需目錄:")
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/")
            missing_dirs.append(dir_path)
    
    # 總結
    print("\n" + "=" * 50)
    if not missing_files and not missing_dirs:
        print("🎉 項目結構完整！所有必需文件和目錄都存在。")
        return True
    else:
        print("⚠️  項目結構不完整！")
        if missing_files:
            print(f"\n缺少文件 ({len(missing_files)}):")
            for file in missing_files:
                print(f"  - {file}")
        if missing_dirs:
            print(f"\n缺少目錄 ({len(missing_dirs)}):")
            for dir in missing_dirs:
                print(f"  - {dir}/")
        return False

def check_python_syntax():
    """檢查 Python 文件語法"""
    project_root = Path(__file__).parent
    python_files = list(project_root.rglob("*.py"))
    
    print(f"\n🐍 檢查 Python 語法 ({len(python_files)} 個文件):")
    
    syntax_errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
            print(f"  ✅ {py_file.relative_to(project_root)}")
        except SyntaxError as e:
            print(f"  ❌ {py_file.relative_to(project_root)}: {e}")
            syntax_errors.append((py_file, e))
        except Exception as e:
            print(f"  ⚠️  {py_file.relative_to(project_root)}: {e}")
    
    return len(syntax_errors) == 0

if __name__ == "__main__":
    print("🚀 YOLOv8s Pipeline 完整性檢查")
    print("=" * 50)
    
    structure_ok = check_project_structure()
    syntax_ok = check_python_syntax()
    
    print("\n" + "=" * 50)
    if structure_ok and syntax_ok:
        print("✅ 檢查完成！項目準備就緒。")
        print("\n使用方式:")
        print("  python main.py --mode full      # 執行完整流程")
        print("  python main.py --mode setup     # 僅環境設置")
        print("  python main.py --mode validate  # 僅數據驗證")
        print("  python main.py --mode optimize  # 僅超參優化")
        print("  python main.py --mode train     # 僅模型訓練")
        sys.exit(0)
    else:
        print("❌ 檢查失敗！請修復上述問題後重試。")
        sys.exit(1)
