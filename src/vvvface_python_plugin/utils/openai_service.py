from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionContentPartTextParam,
    ChatCompletionContentPartImageParam
)
from functools import lru_cache

from ..schemas import LanguageEnum
from ..utils.config import get_config
from ..utils.logger import logger

# 获取配置实例
config = get_config()


class OpenAIClients:
    """OpenAI 客户端管理类"""

    @staticmethod
    @lru_cache()
    def get_qwen_vision_client():
        openai_config = config.openai_config
        return OpenAI(
            api_key=openai_config.get('qwen_vision_api_key'),
            base_url=openai_config.get('qwen_vision_base_url'),
        )

    @staticmethod
    @lru_cache()
    def get_silicon_flow_client():
        openai_config = config.openai_config
        return OpenAI(
            api_key=openai_config.get('silicon_flow_api_key'),
            base_url=openai_config.get('silicon_flow_base_url'),
        )


def _build_vision_message(image_url: str, text_prompt: str, system_prompt: str) -> list:
    """构建视觉消息的公共方法"""
    return [
        ChatCompletionSystemMessageParam(role='system', content=system_prompt),
        ChatCompletionUserMessageParam(
            role='user',
            content=[
                ChatCompletionContentPartTextParam(type='text', text=text_prompt),
                ChatCompletionContentPartImageParam(type='image_url', image_url={'url': image_url})
            ]
        )
    ]


def _build_text_message(user_content: str, system_prompt: str) -> list:
    """构建文本消息的公共方法"""
    return [
        ChatCompletionSystemMessageParam(role='system', content=system_prompt),
        ChatCompletionUserMessageParam(role='user', content=user_content)
    ]


def _get_lang_prompt(language: LanguageEnum, is_video_prompt: bool = False) -> str:
    """获取语言提示"""
    if is_video_prompt:
        return '请用中文生成提示词。' if language == LanguageEnum.ZH else 'Please generate the prompt in English.'
    else:
        return '请用中文自然描述。' if language == LanguageEnum.ZH else 'Please describe naturally in English.'


def analyze_image(image_url: str, language: LanguageEnum = LanguageEnum.ZH) -> str:
    """
    分析图像并生成自然描述文本
    """
    logger.info(f"开始分析图像: {image_url}, 语言: {language}")
    prompt_config = config.prompt_config
    lang_prompt = _get_lang_prompt(language)

    system_prompt = prompt_config.get('analyze_image_system', '').format(lang_prompt=lang_prompt)
    user_prompt = prompt_config.get('analyze_image_user', '')

    messages = _build_vision_message(
        image_url=image_url,
        text_prompt=user_prompt,
        system_prompt=system_prompt
    )

    completions = OpenAIClients.get_qwen_vision_client().chat.completions.create(
        model=config.openai_config.get('qwen_vision_model'),
        messages=messages
    )
    result = completions.choices[0].message.content
    result = result.replace('\n', '').replace('\r', '') if result else result
    logger.info(f"图像分析完成，返回的结果: {result}")
    return result


def analyze_image_with_text(image_url: str, text: str, language: LanguageEnum = LanguageEnum.ZH) -> str:
    """
    分析图像并结合用户文本描述生成融合结果。
    当图像信息与文本冲突时，以文本信息为主。
    （仅调用一次模型）
    """
    logger.info(f"开始图像+文本融合分析: {image_url}, 语言: {language}, 文本: {text[:50]}...")
    prompt_config = config.prompt_config
    lang_prompt = _get_lang_prompt(language)

    image_analysis = analyze_image(image_url, language)

    system_prompt = prompt_config.get('merge_image_text_system', '').format(lang_prompt=lang_prompt)
    user_prompt = prompt_config.get('merge_image_text_user', '').format(image_analysis=image_analysis, text=text)

    messages = _build_text_message(
        user_content=user_prompt,
        system_prompt=system_prompt
    )

    completions = OpenAIClients.get_silicon_flow_client().chat.completions.create(
        model=config.openai_config.get('silicon_flow_model'),
        messages=messages
    )

    result = completions.choices[0].message.content
    result = result.replace('\n', '').replace('\r', '') if result else result
    logger.info(f"图像与文本融合分析完成，返回结果: {result}")
    return result


def text_to_video_prompt(language: LanguageEnum = LanguageEnum.ZH) -> str:
    """
    生成适用于通义万相等视频模型的提示词（无参考图像）
    """
    logger.info(f"开始生成文本到视频提示词，语言: {language}")
    prompt_config = config.prompt_config
    lang_prompt = _get_lang_prompt(language, is_video_prompt=True)

    system_prompt = prompt_config.get('text_to_video_system', '').format(lang_prompt=lang_prompt)
    user_prompt = prompt_config.get('text_to_video_user', '')

    messages = _build_text_message(
        user_content=user_prompt,
        system_prompt=system_prompt
    )

    completions = OpenAIClients.get_silicon_flow_client().chat.completions.create(
        model=config.openai_config.get('silicon_flow_model'),
        messages=messages
    )
    result = completions.choices[0].message.content
    result = result.replace('\n', '').replace('\r', '') if result else result
    logger.info(f"文本到视频提示词生成完成，返回的结果: {result}")
    return result


def image_to_video_prompt(image_url: str, language: LanguageEnum = LanguageEnum.ZH) -> str:
    """
    根据参考图像生成适用于通义万相等视频模型的提示词
    """
    logger.info(f"开始生成图像到视频提示词，图像URL: {image_url}, 语言: {language}")
    prompt_config = config.prompt_config
    lang_prompt = _get_lang_prompt(language, is_video_prompt=True)

    system_prompt = prompt_config.get('image_to_video_system', '').format(lang_prompt=lang_prompt)
    user_prompt = prompt_config.get('image_to_video_user', '')

    messages = _build_vision_message(
        image_url=image_url,
        text_prompt=user_prompt,
        system_prompt=system_prompt
    )

    completions = OpenAIClients.get_qwen_vision_client().chat.completions.create(
        model=config.openai_config.get('qwen_vision_model'),
        messages=messages
    )
    result = completions.choices[0].message.content
    result = result.replace('\n', '').replace('\r', '') if result else result
    logger.info(f"图像到视频提示词生成完成，返回的结果: {result}")
    return result


def translate_text(text: str, target_language: LanguageEnum = LanguageEnum.EN) -> str:
    """
    翻译文本：中文 <-> 英文
    """
    logger.info(f"开始翻译文本，目标语言: {target_language}, 文本长度: {len(text)}")
    prompt_config = config.prompt_config

    if target_language == LanguageEnum.ZH:
        sys_prompt = prompt_config.get('translate_to_zh', '')
    else:
        sys_prompt = prompt_config.get('translate_to_en', '')

    messages = _build_text_message(
        user_content=text,
        system_prompt=sys_prompt
    )

    completions = OpenAIClients.get_silicon_flow_client().chat.completions.create(
        model=config.openai_config.get('silicon_flow_model'),
        messages=messages
    )
    result = completions.choices[0].message.content
    result = result.replace('\n', '').replace('\r', '') if result else result
    logger.info(f"文本翻译完成，返回的结果: {result}")
    return result


def merge_texts(text1: str, text2: str, language: LanguageEnum = LanguageEnum.ZH) -> str:
    """
    合并两段文本为一个统一的描述。
    当两段文本信息有冲突时，以text2为主。
    """
    logger.info(f"开始合并文本，语言: {language}")
    prompt_config = config.prompt_config
    lang_prompt = _get_lang_prompt(language)

    system_prompt = prompt_config.get('merge_texts_system', '').format(lang_prompt=lang_prompt)
    user_prompt = prompt_config.get('merge_texts_user', '').format(text1=text1, text2=text2)

    messages = _build_text_message(
        user_content=user_prompt,
        system_prompt=system_prompt
    )

    completions = OpenAIClients.get_silicon_flow_client().chat.completions.create(
        model=config.openai_config.get('silicon_flow_model'),
        messages=messages
    )

    result = completions.choices[0].message.content
    result = result.replace('\n', '').replace('\r', '') if result else result
    logger.info(f"文本合并完成，返回结果: {result}")
    return result
