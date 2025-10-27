from flask import Flask, request, jsonify
import json
from datetime import datetime
import yyzz_config
import yyzz_request
import yyzz_cached

app = Flask(__name__)


#  统一处理错误，主要是校验json
def create_error_response(code, message):
    return jsonify({"code": code, "error": message})


# 通用的请求处理函数，包含缓存检查和错误处理
def handle_request_with_cache(
    cache_key, cache_file_path, request_func, error_prefix="请求"
):
    """
    通用的请求处理函数，包含缓存检查和错误处理
    :param cache_key: 缓存键
    :param cache_file_path: 缓存文件路径
    :param request_func: 实际发起请求的函数
    :param error_prefix: 错误信息前缀
    """
    cached_response = yyzz_cached.get_cached(cache_key, cache_file_path)
    if cached_response:
        return cached_response

    try:
        response_data = request_func()
        response = json.loads(response_data)

        if response.get("code") == 200:
            yyzz_cached.write_cached(cache_key, response, cache_file_path)
            return response
        return create_error_response(
            400, f"{error_prefix}失败: {response.get('error', '')}"
        )

    except Exception as e:
        return create_error_response(500, f"Error: {str(e)}")


@app.route("/APIRequest", methods=["POST"])
def APIRequest():
    jsondata = request.json
    req_type = jsondata.get("type")
    data = jsondata.get("data")

    if not req_type or not data:
        return create_error_response(400, "请确保传递的参数完整且正确")

    # 图片反推关键词
    if req_type == yyzz_config.REQUEST_TYPE["DESCRIBEIMAGE"]:
        imageUrl = data.get("image_url")
        if not imageUrl:
            return create_error_response(400, "需要提供图片URL")

        cache_key = imageUrl + yyzz_config.QWEN_SYSTEM_PROMPT["DESCRIBEIMAGE"]

        def make_request():
            return yyzz_request.Qwen_request(
                prompt_sys=yyzz_config.QWEN_SYSTEM_PROMPT["DESCRIBEIMAGE"],
                url=imageUrl,
                model=yyzz_config.CLIENT_QWEN["MODEL"],
            )

        return handle_request_with_cache(
            cache_key,
            yyzz_config.CACHE_FILE_PATH["DESCRIBEIMAGE"],
            make_request,
            "图片分析",
        )

    # 虚拟创角
    elif req_type == yyzz_config.REQUEST_TYPE["GENERATECHARACTER"]:
        imageUrl = data.get("image_url")
        content = data.get("content")

        if not imageUrl and not content:
            return create_error_response(400, "需要提供文字描述或图片")

        imageDescribe_content = ""
        # 有图片路径，走图片反推
        if imageUrl:

            def process_image():
                return yyzz_request.Siliconflow_image_request(
                    prompt_sys=yyzz_config.SILICONFLOW_SYSTEM_PROMPT[
                        "CHARACTER_IMAGE_PROCESSING"
                    ],
                    prompt_user=yyzz_config.SILICONFLOW_USER_PROMPT[
                        "CHARACTER_IMAGE_PROCESSING"
                    ],
                    url=imageUrl,
                    model=yyzz_config.CLIENT_SILICONFLOW["CHARACTER_IMAGE_PROCESSING"],
                )

            imageDescribe = handle_request_with_cache(
                imageUrl,
                yyzz_config.CACHE_FILE_PATH["CHARACTER_IMAGE_PROCESSING"],
                process_image,
                "图片处理",
            )

            if imageDescribe.get("code") != 200:
                return imageDescribe

            imageDescribe_content = imageDescribe.get("content")

        cache_key = "[用户输入]:" + content + "[图片描述]:" + imageDescribe_content

        def process_content():
            return yyzz_request.Siliconflow_request(
                prompt_sys=yyzz_config.SILICONFLOW_SYSTEM_PROMPT[
                    "CHARACTER_CONTENT_PROCESSING"
                ],
                prompt_user=cache_key,
                model=yyzz_config.CLIENT_SILICONFLOW["CHARACTER_CONTENT_PROCESSING"],
            )

        return handle_request_with_cache(
            cache_key,
            yyzz_config.CACHE_FILE_PATH["CHARACTER_CONTENT_PROCESSING"],
            process_content,
            "内容处理",
        )

    # 动态润色
    elif req_type == yyzz_config.REQUEST_TYPE["GENERATEDYNAMIC"]:
        content = data.get("content")
        characterDescription = data.get("character_description")

        if not content or not "character_description" in data:
            return create_error_response(400, "动态润色, 请确保传递的参数完整且正确")

        # 第一步：内容扩展
        def expand_content():
            return yyzz_request.Siliconflow_request(
                prompt_sys=yyzz_config.SILICONFLOW_SYSTEM_PROMPT["DYNAMIC_EXPAND"],
                prompt_user=content,
                model=yyzz_config.CLIENT_SILICONFLOW["MODEL_CONTENT_EXPAND"],
            )

        expanded = handle_request_with_cache(
            content,
            yyzz_config.CACHE_FILE_PATH["DYNAMICCONTENTEXPAND"],
            expand_content,
            "内容扩展",
        )

        if expanded.get("code") != 200:
            return expanded

        # 第二步：处理扩展后的内容
        expanded_content = expanded.get("content")
        cache_key = (
            f"user input:{expanded_content}Character traits:{{{characterDescription}}}"
        )

        def process_content():
            return yyzz_request.Siliconflow_request(
                prompt_sys=yyzz_config.SILICONFLOW_SYSTEM_PROMPT["DYNAMIC_PROCESSING"],
                prompt_user=f"user input:{expanded_content}Character traits:{{{characterDescription}}}",
                model=yyzz_config.CLIENT_SILICONFLOW["CHARACTER_CONTENT_PROCESSING"],
            )

        return handle_request_with_cache(
            cache_key,
            yyzz_config.CACHE_FILE_PATH["GENERATEDYNAMIC"],
            process_content,
            "内容处理",
        )

    # 动态不润色，仅翻译成英文
    elif req_type == yyzz_config.REQUEST_TYPE["TRANSLATE"]:
        content = data.get("content")
        characterDescription = data.get("character_description")

        if not content or not characterDescription:
            return create_error_response(400, "动态翻译, 请确保传递的参数完整且正确")

        # 第一步：翻译
        def translate_content():
            return yyzz_request.Siliconflow_request(
                prompt_sys=yyzz_config.SILICONFLOW_SYSTEM_PROMPT["TRANSLATE"],
                prompt_user=content,
                model=yyzz_config.CLIENT_SILICONFLOW["MODEL"],
            )

        translated = handle_request_with_cache(
            content, yyzz_config.CACHE_FILE_PATH["TRANSLATE"], translate_content, "翻译"
        )

        if translated.get("code") != 200:
            return translated

        # 第二步：处理翻译后的内容
        translated_content = translated.get("content")
        cache_key = f"[user input]:{translated_content}[Character traits]:{{{characterDescription}}}"

        def process_translated():
            return yyzz_request.Siliconflow_request(
                prompt_sys=yyzz_config.SILICONFLOW_SYSTEM_PROMPT["DYNAMIC_PROCESSING"],
                prompt_user=cache_key,
                model=yyzz_config.CLIENT_SILICONFLOW["CHARACTER_CONTENT_PROCESSING"],
            )

        return handle_request_with_cache(
            cache_key,
            yyzz_config.CACHE_FILE_PATH["GENERATEDYNAMIC"],
            process_translated,
            "内容处理",
        )

    elif req_type == yyzz_config.REQUEST_TYPE["MIXINUSERPROMPT"]:
        content = data.get("content")
        user_prompt = data.get("user_prompt")

        if not content or not user_prompt:
            return create_error_response(
                400, "用户输入描述注入提示词错误，请确保content与user_prompt存在且完整"
            )

        cache_key = f"[CONTENT_MODEL]:{content}.[USER_CONTENT]:{{{user_prompt}}}"

        def mixin():
            return yyzz_request.Siliconflow_request(
                prompt_sys=yyzz_config.SILICONFLOW_SYSTEM_PROMPT["MIXIN"],
                prompt_user=cache_key,
                model=yyzz_config.CLIENT_SILICONFLOW["CHARACTER_CONTENT_PROCESSING"],
            )

        return handle_request_with_cache(
            cache_key, yyzz_config.CACHE_FILE_PATH["MIXIN"], mixin, "内容处理"
        )

    # 根据图片生成视频提示词
    elif req_type == yyzz_config.REQUEST_TYPE["IMAGE2VIDEOPROMPT"]:
        imageUrl = data.get("image_url")
        if not imageUrl:
            return create_error_response(400, "需要提供图片URL")

        response = yyzz_request.Qwen_request(
            prompt_sys=yyzz_config.SYSTEM_PROMPT["IMAGE2VIDEOPROMPT"],
            url=imageUrl,
            model=yyzz_config.CLIENT_QWEN["MODEL"],
        )
        # response = yyzz_request.Siliconflow_request(
        #     prompt_sys=yyzz_config.SYSTEM_PROMPT["IMAGE2VIDEOPROMPT"],
        #     prompt_user="你需要分析图片,基于图片要素,构建提示词",
        #     model=yyzz_config.CLIENT_SILICONFLOW["GLM-4.1V-9B-Thinking"],
        # )
        return json.loads(response)

    # 随机生成视频提示词
    elif req_type == yyzz_config.REQUEST_TYPE["RANDOMTEXTPROMPT"]:

        response = yyzz_request.Siliconflow_request(
            prompt_sys=yyzz_config.SYSTEM_PROMPT["RANDOMTEXTPROMPT"],
            prompt_user="",  # 此请求不需要用户输入
            model=yyzz_config.CLIENT_SILICONFLOW["MODEL"],
        )
        response = json.loads(response)
        if "content" in response:
            response["content"] = response["content"].strip()
        return response

    else:
        return create_error_response(400, "无效的请求类型")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
