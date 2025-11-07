from pydantic import BaseModel, field_validator
from typing import Optional
from enum import Enum

class LanguageEnum(str, Enum):
    ZH = 'zh'
    EN = 'en'

class AnalyzeImageRequest(BaseModel):
    """图像分析接口请求模型"""
    image_url: str
    language: Optional[LanguageEnum] = LanguageEnum.ZH

    @field_validator('image_url')
    def validate_image_url(cls, v):
        # 去掉前后空格
        v = v.strip() if isinstance(v, str) else v

        # 空字符串检查
        if not v:
            raise ValueError('image_url is required')

        # URL 格式检查
        if not v.startswith(('http://', 'https://')):
            raise ValueError('image_url must be a valid URL')

        return v

class ImageToVideoRequest(BaseModel):
    """图生视频提示词接口请求模型"""
    image_url: str
    language: Optional[LanguageEnum] = LanguageEnum.ZH

    @field_validator('image_url')
    def validate_image_url(cls, v):
        # 去掉前后空格
        v = v.strip() if isinstance(v, str) else v

        # 空字符串检查
        if not v:
            raise ValueError('image_url is required')

        # URL 格式检查
        if not v.startswith(('http://', 'https://')):
            raise ValueError('image_url must be a valid URL')

        return v

class TextToVideoRequest(BaseModel):
    """文生视频提示词接口请求模型"""
    language: Optional[LanguageEnum] = LanguageEnum.ZH


class TranslateTextRequest(BaseModel):
    """翻译接口请求模型"""
    text: str
    target_language: Optional[LanguageEnum] = LanguageEnum.EN

    @field_validator('text')
    def validate_text(cls, v):
        # 去掉前后空格
        v = v.strip() if isinstance(v, str) else v

        # 空字符串检查
        if not v:
            raise ValueError('text is required')

        return v

class AnalyzeImageWithTextRequest(BaseModel):
    """图像分析并结合文本信息接口请求模型"""
    image_url: str
    text: str
    language: Optional[LanguageEnum] = LanguageEnum.ZH

    @field_validator('image_url')
    def validate_image_url(cls, v):
        # 去掉前后空格
        v = v.strip() if isinstance(v, str) else v

        # 空字符串检查
        if not v:
            raise ValueError('image_url is required')

        # URL 格式检查
        if not v.startswith(('http://', 'https://')):
            raise ValueError('image_url must be a valid URL')

        return v

    @field_validator('text')
    def validate_text(cls, v):
        # 去掉前后空格和换行符
        v = v.strip() if isinstance(v, str) else v

        # 空字符串检查
        if not v:
            raise ValueError('text is required')

        return v


class MergeTextRequest(BaseModel):
    """文本合并接口请求模型"""
    text1: str
    text2: str
    language: Optional[LanguageEnum] = LanguageEnum.ZH

    @field_validator('text1')
    def validate_text1(cls, v):
        # 去掉前后空格和换行符
        v = v.strip() if isinstance(v, str) else v

        # 空字符串检查
        if not v:
            raise ValueError('text1 is required')

        return v

    @field_validator('text2')
    def validate_text2(cls, v):
        # 去掉前后空格和换行符
        v = v.strip() if isinstance(v, str) else v

        # 空字符串检查
        if not v:
            raise ValueError('text2 is required')

        return v
