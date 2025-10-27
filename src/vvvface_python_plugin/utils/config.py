import tomllib
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict


class Config:
    """配置管理类"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            # 从项目根目录查找 config.toml
            self.config_path = Path(__file__).parent.parent.parent.parent / 'config.toml'
        else:
            self.config_path = Path(config_path)

        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载 TOML 配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f'配置文件不存在: {self.config_path}')

        with open(self.config_path, 'rb') as f:
            return tomllib.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点分隔的键路径"""
        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def openai_config(self) -> Dict[str, Any]:
        """获取 OpenAI 相关配置"""
        return self.get('openai', {})

    @property
    def prompt_config(self) -> Dict[str, Any]:
        """获取提示词配置"""
        return self.get('prompts', {})


@lru_cache()
def get_config(config_path: str = None) -> Config:
    """获取配置单例"""
    return Config(config_path)
