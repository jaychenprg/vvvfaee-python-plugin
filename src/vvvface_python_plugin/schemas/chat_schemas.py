from pydantic import BaseModel, field_validator
from typing import Optional
from enum import Enum

class LanguageEnum(str, Enum):
    ZH = 'zh'
    EN = 'en'

class AnalyzeImageRequest(BaseModel):
    image_url: str
    language: Optional[LanguageEnum] = LanguageEnum.ZH

    @field_validator("image_url")
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
