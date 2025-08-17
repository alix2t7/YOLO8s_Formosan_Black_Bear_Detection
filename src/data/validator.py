"""
數據驗證器
"""

import os
import yaml
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import json

class DataValidator:
    """數據驗證器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.errors = []
        self.warnings = []
        
    def validate_complete_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """完整數據集驗證"""
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {},
            'recommendations': []
        }
        
        try:
            # 1. 結構驗證
            structure_valid, structure_errors = self._validate_structure(dataset_path)
            if not structure_valid:
                results['errors'].extend(structure_errors)
                results['is_valid'] = False
            
            # 2. 配置文件驗證
            config_valid, config_errors = self._validate_config_file(dataset_path)
            if not config_valid:
                results['errors'].extend(config_errors)
                results['is_valid'] = False
            
            # 3. 數據一致性驗證
            consistency_valid, consistency_errors, consistency_warnings = self._validate_data_consistency(dataset_path)
            if not consistency_valid:
                results['errors'].extend(consistency_errors)
                results['is_valid'] = False
            results['warnings'].extend(consistency_warnings)
            
            # 4. 圖像質量驗證
            quality_warnings = self._validate_image_quality(dataset_path)
            results['warnings'].extend(quality_warnings)
            
            # 5. 標籤格式驗證
            label_valid, label_errors, label_warnings = self._validate_labels(dataset_path)
            if not label_valid:
                results['errors'].extend(label_errors)
                results['is_valid'] = False
            results['warnings'].extend(label_warnings)
            
            # 6. 生成統計信息
            results['statistics'] = self._generate_statistics(dataset_path)
            
            # 7. 生成建議
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            results['errors'].append(f"驗證過程出錯: {str(e)}")
            results['is_valid'] = False
        
        return results
    
    def _validate_structure(self, dataset_path: str) -> Tuple[bool, List[str]]:
        """驗證目錄結構"""
        errors = []
        
        # 檢查主目錄
        if not os.path.exists(dataset_path):
            errors.append(f"數據集目錄不存在: {dataset_path}")
            return False, errors
        
        # 檢查必需的子目錄
        required_dirs = [
            'images/train',
            'images/val', 
            'labels/train',
            'labels/val'
        ]
        
        for dir_path in required_dirs:
            full_path = os.path.join(dataset_path, dir_path)
            if not os.path.exists(full_path):
                errors.append(f"必需目錄不存在: {full_path}")
        
        return len(errors) == 0, errors
    
    def _validate_config_file(self, dataset_path: str) -> Tuple[bool, List[str]]:
        """驗證配置文件"""
        errors = []
        
        # 查找配置文件
        config_files = []
        for file in os.listdir(dataset_path):
            if file.endswith(('.yaml', '.yml')) and 'data' in file.lower():
                config_files.append(os.path.join(dataset_path, file))
        
        if not config_files:
            errors.append("未找到數據集配置文件 (.yaml/.yml)")
            return False, errors
        
        # 驗證配置文件內容
        for config_file in config_files:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # 檢查必需字段
                required_fields = ['train', 'val', 'nc', 'names']
                for field in required_fields:
                    if field not in config:
                        errors.append(f"配置文件缺少字段 '{field}': {config_file}")
                
                # 檢查類別數量一致性
                if 'nc' in config and 'names' in config:
                    if config['nc'] != len(config['names']):
                        errors.append(f"類別數量不一致: nc={config['nc']}, names數量={len(config['names'])}")
                
                # 檢查路徑
                for path_key in ['train', 'val']:
                    if path_key in config:
                        path = config[path_key]
                        if not os.path.isabs(path):
                            # 相對路徑，相對於配置文件目錄
                            path = os.path.join(os.path.dirname(config_file), path)
                        if not os.path.exists(path):
                            errors.append(f"配置文件中的路徑不存在: {path}")
                
            except Exception as e:
                errors.append(f"配置文件解析失敗: {config_file}, 錯誤: {str(e)}")
        
        return len(errors) == 0, errors
    
    def _validate_data_consistency(self, dataset_path: str) -> Tuple[bool, List[str], List[str]]:
        """驗證數據一致性"""
        errors = []
        warnings = []
        
        for split in ['train', 'val']:
            images_dir = os.path.join(dataset_path, f'images/{split}')
            labels_dir = os.path.join(dataset_path, f'labels/{split}')
            
            if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
                continue
            
            # 獲取圖像和標籤文件
            image_files = {os.path.splitext(f)[0] for f in os.listdir(images_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))}
            label_files = {os.path.splitext(f)[0] for f in os.listdir(labels_dir) 
                          if f.endswith('.txt')}
            
            # 檢查缺失的標籤文件
            missing_labels = image_files - label_files
            if missing_labels:
                if len(missing_labels) > 10:
                    errors.append(f"{split}: {len(missing_labels)} 個圖像缺少標籤文件")
                else:
                    for name in list(missing_labels)[:5]:  # 只顯示前5個
                        warnings.append(f"{split}: 圖像 {name} 缺少標籤文件")
            
            # 檢查多餘的標籤文件
            extra_labels = label_files - image_files
            if extra_labels:
                if len(extra_labels) > 10:
                    warnings.append(f"{split}: {len(extra_labels)} 個標籤文件沒有對應圖像")
                else:
                    for name in list(extra_labels)[:5]:
                        warnings.append(f"{split}: 標籤 {name} 沒有對應圖像")
        
        return len(errors) == 0, errors, warnings
    
    def _validate_image_quality(self, dataset_path: str) -> List[str]:
        """驗證圖像質量"""
        warnings = []
        
        for split in ['train', 'val']:
            images_dir = os.path.join(dataset_path, f'images/{split}')
            if not os.path.exists(images_dir):
                continue
            
            image_files = [f for f in os.listdir(images_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            # 檢查少量圖像作為樣本
            sample_size = min(20, len(image_files))
            sample_files = image_files[:sample_size]
            
            corrupted_count = 0
            small_images = 0
            large_images = 0
            
            for image_file in sample_files:
                image_path = os.path.join(images_dir, image_file)
                
                try:
                    # 檢查圖像是否可讀
                    img = cv2.imread(image_path)
                    if img is None:
                        corrupted_count += 1
                        continue
                    
                    height, width = img.shape[:2]
                    
                    # 檢查圖像尺寸
                    if width < 32 or height < 32:
                        small_images += 1
                    elif width > 4096 or height > 4096:
                        large_images += 1
                    
                except Exception:
                    corrupted_count += 1
            
            # 生成警告
            if corrupted_count > 0:
                warnings.append(f"{split}: 發現 {corrupted_count} 個損壞的圖像（樣本檢查）")
            
            if small_images > 0:
                warnings.append(f"{split}: 發現 {small_images} 個過小的圖像（<32px）")
            
            if large_images > 0:
                warnings.append(f"{split}: 發現 {large_images} 個過大的圖像（>4096px）")
        
        return warnings
    
    def _validate_labels(self, dataset_path: str) -> Tuple[bool, List[str], List[str]]:
        """驗證標籤格式"""
        errors = []
        warnings = []
        
        for split in ['train', 'val']:
            labels_dir = os.path.join(dataset_path, f'labels/{split}')
            if not os.path.exists(labels_dir):
                continue
            
            label_files = [f for f in os.listdir(labels_dir) if f.endswith('.txt')]
            
            # 檢查部分標籤文件
            sample_size = min(50, len(label_files))
            sample_files = label_files[:sample_size]
            
            invalid_format_count = 0
            invalid_values_count = 0
            empty_files_count = 0
            
            for label_file in sample_files:
                label_path = os.path.join(labels_dir, label_file)
                
                try:
                    with open(label_path, 'r') as f:
                        lines = f.readlines()
                    
                    if not lines:
                        empty_files_count += 1
                        continue
                    
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        parts = line.split()
                        
                        # 檢查格式：class_id x_center y_center width height
                        if len(parts) != 5:
                            invalid_format_count += 1
                            break
                        
                        try:
                            class_id = int(parts[0])
                            x_center, y_center, width, height = map(float, parts[1:])
                            
                            # 檢查值範圍
                            if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and 
                                   0 <= width <= 1 and 0 <= height <= 1):
                                invalid_values_count += 1
                                break
                            
                            # 檢查類別ID（假設是熊類檢測：0=kumay, 1=not_kumay）
                            if class_id not in [0, 1]:
                                warnings.append(f"{split}: 未知類別ID {class_id} 在 {label_file}:{line_num}")
                        
                        except ValueError:
                            invalid_format_count += 1
                            break
                
                except Exception:
                    invalid_format_count += 1
            
            # 生成錯誤和警告
            if invalid_format_count > 0:
                errors.append(f"{split}: {invalid_format_count} 個標籤文件格式錯誤（樣本檢查）")
            
            if invalid_values_count > 0:
                errors.append(f"{split}: {invalid_values_count} 個標籤文件數值超出範圍（樣本檢查）")
            
            if empty_files_count > 0:
                warnings.append(f"{split}: {empty_files_count} 個空標籤文件")
        
        return len(errors) == 0, errors, warnings
    
    def _generate_statistics(self, dataset_path: str) -> Dict[str, Any]:
        """生成統計信息"""
        stats = {
            'image_counts': {},
            'label_distribution': {},
            'file_sizes': {},
            'class_balance': {}
        }
        
        try:
            total_kumay = 0
            total_not_kumay = 0
            
            for split in ['train', 'val']:
                # 圖像統計
                images_dir = os.path.join(dataset_path, f'images/{split}')
                if os.path.exists(images_dir):
                    image_files = [f for f in os.listdir(images_dir) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    stats['image_counts'][split] = len(image_files)
                else:
                    stats['image_counts'][split] = 0
                
                # 標籤統計
                labels_dir = os.path.join(dataset_path, f'labels/{split}')
                if os.path.exists(labels_dir):
                    kumay_count = 0
                    not_kumay_count = 0
                    
                    for label_file in os.listdir(labels_dir):
                        if not label_file.endswith('.txt'):
                            continue
                        
                        label_path = os.path.join(labels_dir, label_file)
                        try:
                            with open(label_path, 'r') as f:
                                lines = f.readlines()
                            
                            for line in lines:
                                if line.strip():
                                    class_id = int(line.split()[0])
                                    if class_id == 0:
                                        kumay_count += 1
                                    elif class_id == 1:
                                        not_kumay_count += 1
                        except:
                            continue
                    
                    stats['label_distribution'][split] = {
                        'kumay': kumay_count,
                        'not_kumay': not_kumay_count
                    }
                    
                    total_kumay += kumay_count
                    total_not_kumay += not_kumay_count
            
            # 類別平衡
            total_labels = total_kumay + total_not_kumay
            if total_labels > 0:
                stats['class_balance'] = {
                    'kumay_ratio': total_kumay / total_labels,
                    'not_kumay_ratio': total_not_kumay / total_labels,
                    'balance_score': min(total_kumay, total_not_kumay) / max(total_kumay, total_not_kumay) if max(total_kumay, total_not_kumay) > 0 else 0
                }
        
        except Exception as e:
            stats['error'] = f"統計生成失敗: {str(e)}"
        
        return stats
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        # 基於錯誤生成建議
        if results['errors']:
            recommendations.append("🔴 修復所有錯誤後再開始訓練")
        
        # 基於統計生成建議
        stats = results.get('statistics', {})
        
        # 檢查數據量
        image_counts = stats.get('image_counts', {})
        train_count = image_counts.get('train', 0)
        val_count = image_counts.get('val', 0)
        
        if train_count < 100:
            recommendations.append("⚠️  訓練圖像數量較少，建議增加數據或使用數據增強")
        
        if val_count < 20:
            recommendations.append("⚠️  驗證圖像數量較少，建議增加驗證數據")
        
        # 檢查類別平衡
        class_balance = stats.get('class_balance', {})
        balance_score = class_balance.get('balance_score', 1.0)
        
        if balance_score < 0.3:
            recommendations.append("⚠️  類別不平衡嚴重，建議使用類別權重或重採樣")
        elif balance_score < 0.5:
            recommendations.append("💡 類別略有不平衡，可考慮調整類別權重")
        
        # 基於警告生成建議
        if any("空標籤文件" in w for w in results['warnings']):
            recommendations.append("💡 清理空標籤文件或確認是否為負樣本")
        
        if any("損壞" in w for w in results['warnings']):
            recommendations.append("🔧 修復或移除損壞的圖像文件")
        
        if not recommendations:
            recommendations.append("✅ 數據集質量良好，可以開始訓練")
        
        return recommendations
    
    def save_validation_report(self, results: Dict[str, Any], output_path: str) -> None:
        """保存驗證報告"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 驗證報告已保存: {output_path}")
            
        except Exception as e:
            print(f"❌ 保存驗證報告失敗: {str(e)}")
