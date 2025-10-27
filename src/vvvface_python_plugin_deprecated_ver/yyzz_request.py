from flask import jsonify
import json
from openai import OpenAI
import yyzz_config
import yyzz_cached


# 初始化客户端
def create_client(config):
    return OpenAI(api_key=config["API_KEY"], base_url=config["BASE_URL"])


# 创建两个客户端实例
Client_Qwen = create_client(yyzz_config.CLIENT_QWEN)
Client_Siliconflow = create_client(yyzz_config.CLIENT_SILICONFLOW)


def create_response(code, content, is_error=False):
    """创建统一的响应格式"""
    response = {"code": code, "content" if not is_error else "error": content}
    return json.dumps(response, ensure_ascii=False, indent=4)


def process_completion(completion):
    """处理API返回结果"""
    result = completion.model_dump_json()
    result_dict = json.loads(result)
    content = result_dict["choices"][0]["message"]["content"]
    return create_response(200, content)


def handle_request(request_func):
    """统一的请求处理装饰器"""
    try:
        completion = request_func()
        return process_completion(completion)
    except Exception as e:
        return create_response(500, f"Error: {str(e)}", True)


def Qwen_request(prompt_sys, url, model):
    """通义千问图像请求"""

    def make_request():
        return Client_Qwen.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt_sys},
                {
                    "role": "user",
                    "content": [{"type": "image_url", "image_url": {"url": url}}],
                },
            ],
        )

    return handle_request(make_request)


def Siliconflow_request(prompt_sys, prompt_user, model):
    """硅基流动文本请求"""

    def make_request():
        return Client_Siliconflow.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt_sys},
                {"role": "user", "content": prompt_user},
            ],
        )

    return handle_request(make_request)


def Siliconflow_image_request(prompt_sys, prompt_user, url, model):
    """硅基流动图像请求"""

    def make_request():
        return Client_Siliconflow.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt_sys},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_user},
                        {"type": "image_url", "image_url": {"url": url}},
                    ],
                },
            ],
        )

    return handle_request(make_request)
