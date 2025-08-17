"""
Optuna 超參數優化器
基於 YOLOv8_Optuna_Optimizer.py
"""

import optuna
import yaml
import json
import os
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging

from ultralytics import YOLO
from ..utils.logger import YOLOLogger
from ..utils.gpu_manager import GPUManager
from ..utils.file_manager import FileManager
from ..environment.manager import EnvironmentManager

class OptunaOptimizer:
    """Optuna 超參數優化器"""
    
    def __init__(self, config_path: str, logger: Optional[YOLOLogger] = None):
        self.config_path = config_path
        self.logger = logger or YOLOLogger()
        self.file_manager = FileManager()
        self.gpu_manager = GPUManager()
        self.env_manager = EnvironmentManager()
        
        # 加載配置
        self.base_config = self.file_manager.load_config("config/base_config.yaml")
        self.optuna_config = self.file_manager.load_config("config/optuna_config.yaml")
        
        # 創建結果目錄
        self.results_dir = os.path.join("results", "optimization", self.file_manager.create_timestamp())
        os.makedirs(self.results_dir, exist_ok=True)
        
        # 優化歷史
        self.trials_history = []
        self.best_params = None
        self.best_score = 0.0
        
        # 配置 optuna 日誌
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    
    def objective(self, trial: optuna.trial.Trial) -> float:
        """Optuna 目標函數"""
        try:
            # 建議超參數
            params = self._suggest_parameters(trial)
            
            self.logger.info(f"Trial {trial.number}: {params}")
            
            # 創建訓練配置
            train_config = self._create_train_config(params)
            
            # 訓練模型
            score = self._train_and_evaluate(train_config, trial.number)
            
            # 記錄試驗結果
            self._record_trial(trial.number, params, score)
            
            # 更新最佳結果
            if score > self.best_score:
                self.best_score = score
                self.best_params = params
                self._save_best_params()
            
            return score
            
        except Exception as e:
            self.logger.error(f"Trial {trial.number} 失敗: {str(e)}")
            return 0.0
    
    def _suggest_parameters(self, trial: optuna.trial.Trial) -> Dict[str, Any]:
        """建議超參數"""
        params = {}
        
        # 從配置中獲取搜索範圍
        search_space = self.optuna_config.get('search_space', {})
        
        # 學習率
        if 'lr0' in search_space:
            lr_config = search_space['lr0']
            params['lr0'] = trial.suggest_float(
                'lr0',
                lr_config['min'],
                lr_config['max'],
                log=lr_config.get('log', True)
            )
        
        # 權重衰減
        if 'weight_decay' in search_space:
            wd_config = search_space['weight_decay']
            params['weight_decay'] = trial.suggest_float(
                'weight_decay',
                wd_config['min'],
                wd_config['max'],
                log=wd_config.get('log', True)
            )
        
        # 動量
        if 'momentum' in search_space:
            momentum_config = search_space['momentum']
            params['momentum'] = trial.suggest_float(
                'momentum',
                momentum_config['min'],
                momentum_config['max']
            )
        
        # Warmup epochs
        if 'warmup_epochs' in search_space:
            warmup_config = search_space['warmup_epochs']
            params['warmup_epochs'] = trial.suggest_int(
                'warmup_epochs',
                warmup_config['min'],
                warmup_config['max']
            )
        
        # Box loss gain
        if 'box' in search_space:
            box_config = search_space['box']
            params['box'] = trial.suggest_float(
                'box',
                box_config['min'],
                box_config['max']
            )
        
        # Classification loss gain
        if 'cls' in search_space:
            cls_config = search_space['cls']
            params['cls'] = trial.suggest_float(
                'cls',
                cls_config['min'],
                cls_config['max']
            )
        
        # DFL loss gain
        if 'dfl' in search_space:
            dfl_config = search_space['dfl']
            params['dfl'] = trial.suggest_float(
                'dfl',
                dfl_config['min'],
                dfl_config['max']
            )
        
        return params
    
    def _create_train_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """創建訓練配置"""
        config = {
            'model': self.optuna_config['fixed_params']['model'],
            'data': self.base_config['dataset']['config_path'],
            'epochs': self.optuna_config['fixed_params']['epochs'],
            'batch': self.optuna_config['fixed_params']['batch_size'],
            'imgsz': self.base_config['model']['image_size'],
            'device': self.gpu_manager.get_device(),
            'workers': self.base_config['training']['workers'],
            'project': os.path.join(self.results_dir, "trials"),
            'name': f"trial_{time.time()}",
            'exist_ok': True,
            'verbose': False,
            'save': False,  # 不保存檢查點以節省空間
            'val': True,
            'plots': False,  # 不生成圖表以節省時間
        }
        
        # 添加優化參數
        config.update(params)
        
        return config
    
    def _train_and_evaluate(self, config: Dict[str, Any], trial_num: int) -> float:
        """訓練並評估模型"""
        try:
            # 創建模型
            model = YOLO(config['model'])
            
            # 訓練
            results = model.train(**config)
            
            # 驗證
            val_results = model.val(data=config['data'], verbose=False)
            
            # 計算熊類檢測分數（基於原始代碼邏輯）
            score = self._calculate_bear_score(val_results)
            
            self.logger.info(f"Trial {trial_num} 完成，分數: {score:.4f}")
            
            return score
            
        except Exception as e:
            self.logger.error(f"訓練失敗: {str(e)}")
            return 0.0
    
    def _calculate_bear_score(self, val_results) -> float:
        """計算熊類檢測分數"""
        try:
            # 獲取驗證結果
            metrics = val_results.results_dict
            
            # 基於原始代碼的評分邏輯
            # 重點關注 mAP50 和 mAP50-95
            map50 = metrics.get('metrics/mAP50(B)', 0.0)
            map50_95 = metrics.get('metrics/mAP50-95(B)', 0.0)
            
            # 加權分數（原始代碼傾向於 mAP50）
            score = 0.7 * map50 + 0.3 * map50_95
            
            return float(score)
            
        except Exception as e:
            self.logger.error(f"計算分數失敗: {str(e)}")
            return 0.0
    
    def _record_trial(self, trial_num: int, params: Dict[str, Any], score: float) -> None:
        """記錄試驗結果"""
        trial_record = {
            'trial': trial_num,
            'timestamp': datetime.now().isoformat(),
            'parameters': params,
            'score': score,
            'is_best': score > self.best_score
        }
        
        self.trials_history.append(trial_record)
        
        # 保存到文件
        history_file = os.path.join(self.results_dir, "trials_history.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.trials_history, f, indent=2, ensure_ascii=False)
    
    def _save_best_params(self) -> None:
        """保存最佳參數"""
        best_params_file = os.path.join(self.results_dir, "best_params.yaml")
        best_result = {
            'best_score': self.best_score,
            'best_parameters': self.best_params,
            'timestamp': datetime.now().isoformat(),
            'total_trials': len(self.trials_history)
        }
        
        with open(best_params_file, 'w', encoding='utf-8') as f:
            yaml.dump(best_result, f, default_flow_style=False, allow_unicode=True)
        
        self.logger.info(f"💾 已保存最佳參數，分數: {self.best_score:.4f}")
    
    def optimize(self, n_trials: Optional[int] = None) -> Dict[str, Any]:
        """執行超參數優化"""
        if n_trials is None:
            n_trials = self.optuna_config.get('n_trials', 50)
        
        self.logger.info(f"🔍 開始超參數優化，共 {n_trials} 次試驗")
        
        # 創建研究
        study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=42),
            pruner=optuna.pruners.MedianPruner()
        )
        
        # 開始優化
        start_time = time.time()
        
        try:
            study.optimize(self.objective, n_trials=n_trials)
        except KeyboardInterrupt:
            self.logger.warning("⚠️  優化被用戶中斷")
        except Exception as e:
            self.logger.error(f"優化過程出錯: {str(e)}")
        
        # 優化完成
        elapsed_time = time.time() - start_time
        
        # 保存最終結果
        final_results = self._save_optimization_results(study, elapsed_time)
        
        self.logger.info(f"✅ 優化完成！用時: {elapsed_time/3600:.2f} 小時")
        self.logger.info(f"🏆 最佳分數: {study.best_value:.4f}")
        
        return final_results
    
    def _get_parameter_importance(self, study: optuna.Study) -> Dict[str, float]:
        """獲取參數重要性 - 兼容不同版本的 Optuna"""
        try:
            # 嘗試使用 optuna.importance 模組
            if hasattr(optuna, 'importance'):
                return optuna.importance.get_param_importances(study)
            else:
                # 如果不可用，返回空字典
                return {}
        except Exception as e:
            self.logger.warning(f"無法計算參數重要性: {e}")
            return {}
    
    def _save_optimization_results(self, study: optuna.Study, elapsed_time: float) -> Dict[str, Any]:
        """保存優化結果"""
        results = {
            'optimization_summary': {
                'total_trials': len(study.trials),
                'best_score': study.best_value,
                'best_params': study.best_params,
                'elapsed_time_hours': elapsed_time / 3600,
                'timestamp': datetime.now().isoformat()
            },
            'study_statistics': {
                'completed_trials': len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]),
                'failed_trials': len([t for t in study.trials if t.state == optuna.trial.TrialState.FAIL]),
                'pruned_trials': len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])
            },
            'parameter_importance': self._get_parameter_importance(study) if len(study.trials) > 1 else {}
        }
        
        # 保存完整結果
        results_file = os.path.join(self.results_dir, "optimization_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 保存最佳參數到主配置目錄
        best_params_path = "config/best_params.yaml"
        self.file_manager.save_config(study.best_params, best_params_path)
        
        return results
    
    def get_best_parameters(self) -> Optional[Dict[str, Any]]:
        """獲取最佳參數"""
        return self.best_params
    
    def load_best_parameters(self, params_path: str = "config/best_params.yaml") -> Dict[str, Any]:
        """加載最佳參數"""
        if os.path.exists(params_path):
            return self.file_manager.load_config(params_path)
        return {}
