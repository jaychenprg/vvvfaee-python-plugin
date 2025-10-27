import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from ..utils.config import get_config


def setup_logger(name: str = 'vvvface', log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    设置带有日志轮转功能的日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径，默认为 None，则会自动创建 logs 目录
        level: 日志级别，默认为 INFO
    
    Returns:
        配置好的 Logger 实例
    """
    # 创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 如果没有指定日志文件，则使用默认路径
    if log_file is None:
        # 在项目根目录下创建 logs 文件夹
        project_root = Path(__file__).parent.parent.parent
        logs_dir = project_root / 'logs'
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / 'app.log'
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建文件处理器，启用日志轮转
    # 当文件大小达到 10MB 时轮转，保留最近 5 个日志文件
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # 创建控制台处理器
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(level)
    # console_handler.setFormatter(formatter)
    
    # 添加处理器到 logger
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)
    
    return logger


# 获取全局配置实例
config = get_config()

# 创建全局日志记录器实例
logger = setup_logger()
