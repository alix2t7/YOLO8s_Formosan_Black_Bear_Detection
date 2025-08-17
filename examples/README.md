# 🚀 YOLOv8s 台灣黑熊檢測系統使用範例

## 基本使用範例

### 1. 快速開始訓練

```python
# basic_example.py
from src.training.trainer import YOLOv8sTrainer
from src.utils.logger import YOLOLogger

# 初始化日誌和訓練器
logger = YOLOLogger()
trainer = YOLOv8sTrainer()

# 執行訓練
logger.info("開始訓練台灣黑熊檢測模型...")
results = trainer.run_complete_training()

if results:
    logger.info(f"訓練完成！最終性能: {results['final_metrics']}")
else:
    logger.error("訓練失敗")
```

### 2. 自定義超參數優化

```python
# optimization_example.py
from src.optimization.optuna_optimizer import OptunaOptimizer

# 初始化優化器
optimizer = OptunaOptimizer(config_path="config/optuna_config.yaml")

# 自定義優化參數
def objective(trial):
    # 定義搜索空間
    lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])
    
    # 執行訓練並返回性能指標
    trainer = YOLOv8sTrainer()
    results = trainer.train_with_params(lr=lr, batch_size=batch_size)
    
    return results['mAP50']

# 執行優化
study = optimizer.optimize(n_trials=100, objective_func=objective)
best_params = study.best_params
print(f"最佳參數: {best_params}")
```

### 3. 數據驗證和品質檢查

```python
# data_validation_example.py
from src.data.validator import DataValidator

# 初始化驗證器
validator = DataValidator()

# 執行完整數據驗證
dataset_path = "./data"
validation_results = validator.validate_complete_dataset(dataset_path)

# 檢查結果
if validation_results['is_valid']:
    print("✅ 數據集驗證通過")
    print(f"📊 統計資訊: {validation_results['statistics']}")
else:
    print("❌ 數據集驗證失敗")
    for error in validation_results['errors']:
        print(f"   - {error}")

# 保存驗證報告
validator.save_validation_report(validation_results, "data_validation_report.json")
```

### 4. 環境檢測和設置

```python
# environment_example.py
from src.environment.setup import EnvironmentSetup
from src.environment.manager import EnvironmentManager

# 環境設置
env_setup = EnvironmentSetup()

# 檢測平台類型
print(f"檢測到平台: {env_setup.platform_type}")

# 安裝必要套件
required_packages = ['torch', 'ultralytics', 'optuna']
install_results = env_setup.install_packages(required_packages)

# 設置 CUDA 環境
cuda_info = env_setup.setup_cuda_environment()
print(f"CUDA 可用: {cuda_info['available']}")

# 環境管理和監控
env_manager = EnvironmentManager()
system_info = env_manager.get_system_info()
print(f"系統資訊: {system_info}")
```

## 高級使用範例

### 1. 自定義訓練配置

```python
# custom_training_config.py

# 創建自定義配置
custom_config = {
    "model": {
        "name": "yolov8s.pt",
        "input_size": 640,
        "classes": ["kumay", "not_kumay"]
    },
    "training": {
        "epochs": 300,
        "batch_size": 16,
        "learning_rate": 0.01,
        "optimizer": "AdamW",
        "scheduler": "cosine"
    },
    "data_augmentation": {
        "mosaic": 1.0,
        "mixup": 0.1,
        "copy_paste": 0.3,
        "hsv_h": 0.015,
        "hsv_s": 0.7,
        "hsv_v": 0.4
    },
    "validation": {
        "val_split": 0.2,
        "save_period": 10,
        "patience": 50
    }
}

# 使用自定義配置訓練
from src.training.trainer import YOLOv8sTrainer

trainer = YOLOv8sTrainer(config=custom_config)
results = trainer.run_complete_training()
```

### 2. 批量實驗管理

```python
# batch_experiments.py
import itertools
from src.utils.logger import YOLOLogger

logger = YOLOLogger()

# 定義實驗參數
learning_rates = [0.001, 0.01, 0.1]
batch_sizes = [8, 16, 32]
optimizers = ["Adam", "AdamW", "SGD"]

# 執行批量實驗
results = []
for lr, bs, opt in itertools.product(learning_rates, batch_sizes, optimizers):
    logger.info(f"實驗: lr={lr}, batch_size={bs}, optimizer={opt}")
    
    config = {
        "training": {
            "learning_rate": lr,
            "batch_size": bs,
            "optimizer": opt
        }
    }
    
    trainer = YOLOv8sTrainer(config=config)
    result = trainer.run_complete_training()
    
    results.append({
        "params": {"lr": lr, "batch_size": bs, "optimizer": opt},
        "performance": result['final_metrics']
    })

# 分析最佳結果
best_result = max(results, key=lambda x: x['performance']['mAP50'])
logger.info(f"最佳實驗結果: {best_result}")
```

### 3. 模型推理和部署

```python
# inference_example.py
import cv2
from ultralytics import YOLO

# 加載訓練好的模型
model = YOLO("results/training/best.pt")

# 單張圖像推理
image_path = "test_image.jpg"
results = model(image_path)

# 處理結果
for r in results:
    # 獲取邊界框
    boxes = r.boxes
    for box in boxes:
        # 提取座標和置信度
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        confidence = box.conf[0].cpu().numpy()
        class_id = box.cls[0].cpu().numpy()
        
        # 判斷是否為台灣黑熊
        if class_id == 0 and confidence > 0.5:  # kumay
            print(f"檢測到台灣黑熊！置信度: {confidence:.2f}")
        
    # 保存結果圖像
    annotated_frame = r.plot()
    cv2.imwrite("detection_result.jpg", annotated_frame)

# 批量推理
image_folder = "test_images/"
results = model(image_folder)

# 視頻推理
video_path = "test_video.mp4"
results = model(video_path, stream=True)

for r in results:
    # 處理每一幀的結果
    annotated_frame = r.plot()
    # 顯示或保存
```

## 配置範例

### 完整的訓練配置 (training_config.yaml)

```yaml
# 模型配置
model:
  name: "yolov8s.pt"
  input_size: 640
  classes: ["kumay", "not_kumay"]
  
# 訓練配置
training:
  epochs: 300
  batch_size: 16
  learning_rate: 0.01
  optimizer: "AdamW"
  scheduler: "cosine"
  warmup_epochs: 3
  warmup_momentum: 0.8
  warmup_bias_lr: 0.1
  
# 數據增強
augmentation:
  mosaic: 1.0
  mixup: 0.1
  copy_paste: 0.3
  hsv_h: 0.015
  hsv_s: 0.7
  hsv_v: 0.4
  degrees: 10.0
  translate: 0.1
  scale: 0.9
  shear: 2.0
  perspective: 0.0
  flipud: 0.0
  fliplr: 0.5
  
# 驗證配置
validation:
  val_split: 0.2
  save_period: 10
  patience: 50
  min_delta: 0.001
  
# 硬體配置
hardware:
  device: "auto"  # auto, cpu, 0, 1, 2, ...
  workers: 8
  amp: true  # Automatic Mixed Precision
```

### Optuna 優化配置 (optuna_config.yaml)

```yaml
# 優化配置
optimization:
  n_trials: 100
  timeout: 3600  # 1 hour
  direction: "maximize"
  metric: "mAP50"
  
# 搜索空間
search_space:
  learning_rate:
    type: "float"
    low: 1e-5
    high: 1e-1
    log: true
    
  batch_size:
    type: "categorical"
    choices: [8, 16, 32, 64]
    
  optimizer:
    type: "categorical"
    choices: ["Adam", "AdamW", "SGD", "RMSprop"]
    
  weight_decay:
    type: "float"
    low: 1e-6
    high: 1e-2
    log: true
    
  momentum:
    type: "float"
    low: 0.8
    high: 0.99
    
# Pruner 配置
pruner:
  type: "MedianPruner"
  n_startup_trials: 5
  n_warmup_steps: 10
  interval_steps: 1
```

## 故障排除範例

### 常見問題解決

```python
# troubleshooting_example.py
from src.utils.logger import YOLOLogger
from src.environment.setup import EnvironmentSetup

logger = YOLOLogger()

# 檢查環境問題
def diagnose_environment():
    env_setup = EnvironmentSetup()
    
    # 檢查 Python 版本
    import sys
    logger.info(f"Python 版本: {sys.version}")
    
    # 檢查 CUDA
    cuda_info = env_setup.setup_cuda_environment()
    if not cuda_info['available']:
        logger.warning("CUDA 不可用，將使用 CPU 訓練")
        logger.info("建議檢查 CUDA 和 cuDNN 安裝")
    
    # 檢查記憶體
    import psutil
    memory = psutil.virtual_memory()
    logger.info(f"可用記憶體: {memory.available / 1024**3:.1f} GB")
    
    if memory.available < 8 * 1024**3:  # 8GB
        logger.warning("記憶體可能不足，建議降低 batch_size")

# 處理常見錯誤
def handle_common_errors():
    try:
        # 您的訓練代碼
        pass
    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
            logger.error("GPU 記憶體不足")
            logger.info("建議: 降低 batch_size 或使用 gradient_accumulation")
        elif "No such file or directory" in str(e):
            logger.error("檔案路徑錯誤")
            logger.info("建議: 檢查數據集路徑和配置檔案")
    except ImportError as e:
        logger.error(f"套件導入錯誤: {e}")
        logger.info("建議: pip install -r requirements.txt")

if __name__ == "__main__":
    diagnose_environment()
    handle_common_errors()
```

這些範例展示了系統的完整功能和靈活性，您可以根據需要調整和擴展！
