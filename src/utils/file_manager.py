"""
文件管理模組
提供文件和目錄管理功能
"""

import os
import shutil
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import hashlib


class FileManager:
    """文件管理器"""

    def __init__(self, base_dir: Union[str, Path] = "."):
        self.base_dir = Path(base_dir).resolve()
        self.ensure_dir(self.base_dir)

    def ensure_dir(self, path: Union[str, Path]) -> Path:
        """確保目錄存在"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_timestamp(self) -> str:
        """創建時間戳字符串"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def create_project_structure(
        self, project_dir: Union[str, Path]
    ) -> Dict[str, Path]:
        """創建項目目錄結構"""
        project_dir = Path(project_dir)

        structure = {
            "root": project_dir,
            "config": project_dir / "config",
            "data": project_dir / "data",
            "models": project_dir / "models",
            "results": project_dir / "results",
            "logs": project_dir / "logs",
            "cache": project_dir / "cache",
            "temp": project_dir / "temp",
        }

        # 創建所有目錄
        for name, path in structure.items():
            self.ensure_dir(path)

        return structure

    def save_config(
        self, config: Dict[str, Any], filepath: Union[str, Path], format: str = "auto"
    ) -> Path:
        """保存配置文件"""
        filepath = Path(filepath)
        self.ensure_dir(filepath.parent)

        # 自動判斷格式
        if format == "auto":
            format = filepath.suffix.lower().lstrip(".")

        if format in ["yaml", "yml"]:
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(
                    config, f, default_flow_style=False, allow_unicode=True, indent=2
                )
        elif format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支援的格式: {format}")

        return filepath

    def load_config(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """載入配置文件"""
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"配置文件不存在: {filepath}")

        suffix = filepath.suffix.lower()

        with open(filepath, "r", encoding="utf-8") as f:
            if suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            elif suffix == ".json":
                return json.load(f)
            else:
                raise ValueError(f"不支援的配置文件格式: {suffix}")

    def backup_file(
        self, filepath: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None
    ) -> Path:
        """備份文件"""
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        if backup_dir is None:
            backup_dir = filepath.parent / "backup"

        backup_dir = Path(backup_dir)
        self.ensure_dir(backup_dir)

        # 生成備份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
        backup_path = backup_dir / backup_name

        shutil.copy2(filepath, backup_path)
        return backup_path

    def clean_directory(
        self,
        directory: Union[str, Path],
        patterns: List[str] = None,
        older_than_days: Optional[int] = None,
    ) -> List[Path]:
        """清理目錄"""
        directory = Path(directory)
        removed_files = []

        if not directory.exists():
            return removed_files

        if patterns is None:
            patterns = ["*.tmp", "*.temp", "*~", ".DS_Store"]

        # 計算時間閾值
        time_threshold = None
        if older_than_days is not None:
            from datetime import timedelta

            time_threshold = datetime.now() - timedelta(days=older_than_days)

        for pattern in patterns:
            for filepath in directory.rglob(pattern):
                try:
                    # 檢查文件年齡
                    if time_threshold is not None:
                        file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                        if file_time > time_threshold:
                            continue

                    if filepath.is_file():
                        filepath.unlink()
                        removed_files.append(filepath)
                    elif filepath.is_dir():
                        shutil.rmtree(filepath)
                        removed_files.append(filepath)

                except OSError:
                    pass  # 忽略無法刪除的文件

        return removed_files

    def get_directory_size(self, directory: Union[str, Path]) -> Dict[str, Any]:
        """獲取目錄大小信息"""
        directory = Path(directory)

        if not directory.exists():
            return {"exists": False}

        total_size = 0
        file_count = 0
        dir_count = 0

        for item in directory.rglob("*"):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                    file_count += 1
                except OSError:
                    pass
            elif item.is_dir():
                dir_count += 1

        return {
            "exists": True,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / 1024**2,
            "total_size_gb": total_size / 1024**3,
            "file_count": file_count,
            "directory_count": dir_count,
        }

    def find_files(
        self, directory: Union[str, Path], pattern: str = "*", recursive: bool = True
    ) -> List[Path]:
        """查找文件"""
        directory = Path(directory)

        if not directory.exists():
            return []

        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))

    def copy_directory(
        self, src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False
    ) -> Path:
        """複製目錄"""
        src = Path(src)
        dst = Path(dst)

        if not src.exists():
            raise FileNotFoundError(f"源目錄不存在: {src}")

        if dst.exists() and not overwrite:
            raise FileExistsError(f"目標目錄已存在: {dst}")

        if dst.exists() and overwrite:
            shutil.rmtree(dst)

        shutil.copytree(src, dst)
        return dst

    def create_symlink(self, src: Union[str, Path], dst: Union[str, Path]) -> Path:
        """創建符號連結"""
        src = Path(src)
        dst = Path(dst)

        if not src.exists():
            raise FileNotFoundError(f"源路徑不存在: {src}")

        self.ensure_dir(dst.parent)

        try:
            dst.symlink_to(src)
            return dst
        except OSError as e:
            # Windows 或權限問題，嘗試複製
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            return dst

    def calculate_checksum(
        self, filepath: Union[str, Path], algorithm: str = "md5"
    ) -> str:
        """計算文件校驗和"""
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        hash_obj = hashlib.new(algorithm)

        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def compress_directory(
        self,
        directory: Union[str, Path],
        output_file: Union[str, Path],
        format: str = "zip",
    ) -> Path:
        """壓縮目錄"""
        directory = Path(directory)
        output_file = Path(output_file)

        if not directory.exists():
            raise FileNotFoundError(f"目錄不存在: {directory}")

        self.ensure_dir(output_file.parent)

        # 移除副檔名以讓 shutil 自動添加
        base_name = str(output_file.with_suffix(""))

        shutil.make_archive(base_name, format, directory)

        # 返回實際創建的文件路徑
        if format == "zip":
            return Path(f"{base_name}.zip")
        elif format == "tar":
            return Path(f"{base_name}.tar")
        elif format == "gztar":
            return Path(f"{base_name}.tar.gz")
        else:
            return Path(f"{base_name}.{format}")

    def extract_archive(
        self, archive_file: Union[str, Path], extract_to: Union[str, Path]
    ) -> Path:
        """解壓縮文件"""
        archive_file = Path(archive_file)
        extract_to = Path(extract_to)

        if not archive_file.exists():
            raise FileNotFoundError(f"壓縮文件不存在: {archive_file}")

        self.ensure_dir(extract_to)

        shutil.unpack_archive(archive_file, extract_to)
        return extract_to

    def create_manifest(self, directory: Union[str, Path]) -> Dict[str, Any]:
        """創建目錄清單"""
        directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"目錄不存在: {directory}")

        manifest = {
            "created_at": datetime.now().isoformat(),
            "directory": str(directory),
            "total_size": self.get_directory_size(directory),
            "files": [],
        }

        for filepath in directory.rglob("*"):
            if filepath.is_file():
                try:
                    stat = filepath.stat()
                    file_info = {
                        "path": str(filepath.relative_to(directory)),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "checksum": self.calculate_checksum(filepath),
                    }
                    manifest["files"].append(file_info)
                except OSError:
                    pass

        return manifest

    def save_manifest(
        self,
        directory: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
    ) -> Path:
        """保存目錄清單"""
        if output_file is None:
            directory_name = Path(directory).name
            output_file = Path(directory) / f"{directory_name}_manifest.json"

        manifest = self.create_manifest(directory)
        return self.save_config(manifest, output_file, "json")


# 全域文件管理器實例
_file_manager: Optional[FileManager] = None


def get_file_manager() -> FileManager:
    """獲取文件管理器實例"""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileManager()
    return _file_manager
