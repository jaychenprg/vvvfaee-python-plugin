from copyreg import constructor

from aiohttp import web
from pydantic import ValidationError

from ..utils.logger import logger
from ..utils.openai_service import analyze_image, analyze_image_with_text, image_to_video_prompt, text_to_video_prompt, translate_text, merge_texts
from ..schemas import AnalyzeImageRequest, AnalyzeImageWithTextRequest, ImageToVideoRequest, TextToVideoRequest, TranslateTextRequest, MergeTextRequest

routes = web.RouteTableDef()

@routes.get('/analyze_image')
def analyze_image_route(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)
        # 记录请求日志
        logger.info(f"处理 analyze_image 请求: {request_data}")
        # 验证参数
        params = AnalyzeImageRequest(**request_data)
    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        logger.error(f"参数验证失败: {error_message}")
        return web.json_response({'code': -1, 'msg': error_message}, status=400)
    except Exception as e:
        # 其他错误
        logger.error(f"处理 analyze_image 请求时发生未知错误: {str(e)}")
        return web.json_response({'code': -1, 'msg': str(e)}, status=500)

    # 处理请求
    content = analyze_image(params.image_url, params.language)
    logger.info("成功处理 analyze_image 请求")
    return web.json_response({
        'code': 0,
        'data': {
            'content': content,
        },
        'msg': 'analyze_image',
    })

@routes.get('/analyze_image_with_text')
def analyze_image_with_text_route(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)
        # 记录请求日志
        logger.info(f"处理 analyze_image_with_text 请求: {request_data}")
        # 验证参数
        params = AnalyzeImageWithTextRequest(**request_data)
    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        logger.error(f"参数验证失败: {error_message}")
        return web.json_response({'code': -1, 'error': error_message}, status=400)
    except Exception as e:
        # 其他错误
        logger.error(f"处理 analyze_image_with_text 请求时发生未知错误: {str(e)}")
        return web.json_response({'code': -1, 'error': str(e)}, status=500)

    # 处理请求
    content = analyze_image_with_text(params.image_url, params.text, params.language)
    logger.info("成功处理 analyze_image_with_text 请求")
    return web.json_response({
        'code': 0,
        'data': {
            'content': content,
        },
        'msg': 'analyze_image_with_text',
    })

@routes.get('/image_to_video')
def image_to_video_route(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)
        # 记录请求日志
        logger.info(f"处理 image_to_video 请求: {request_data}")
        # 验证参数
        params = ImageToVideoRequest(**request_data)
    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        logger.error(f"参数验证失败: {error_message}")
        return web.json_response({'code': -1, 'error': error_message}, status=400)
    except Exception as e:
        # 其他错误
        logger.error(f"处理 image_to_video 请求时发生未知错误: {str(e)}")
        return web.json_response({'code': -1, 'error': str(e)}, status=500)

    content = image_to_video_prompt(params.image_url, params.language)
    logger.info("成功处理 image_to_video 请求")
    return web.json_response({
        'code': 0,
        'data': {
            'content': content,
        },
        'msg': 'image_to_video',
    })

@routes.get('/text_to_video')
def text_to_video_route(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)
        # 记录请求日志
        logger.info(f"处理 text_to_video 请求: {request_data}")
        # 验证参数
        params = TextToVideoRequest(**request_data)
    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        logger.error(f"参数验证失败: {error_message}")
        return web.json_response({'code': -1, 'error': error_message}, status=400)
    except Exception as e:
        # 其他错误
        logger.error(f"处理 text_to_video 请求时发生未知错误: {str(e)}")
        return web.json_response({'code': -1, 'error': str(e)}, status=500)

    content = text_to_video_prompt(params.language)
    logger.info("成功处理 text_to_video 请求")
    return web.json_response({
        'code': 0,
        'data': {
            'content': content,
        },
        'msg': 'text_to_video',
    })

@routes.get('/translate_text')
def translate_text_route(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)
        # 记录请求日志
        logger.info(f"处理 translate_text 请求: {request_data}")
        # 验证参数
        params = TranslateTextRequest(**request_data)
    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        logger.error(f"参数验证失败: {error_message}")
        return web.json_response({'code': -1, 'error': error_message}, status=400)
    except Exception as e:
        # 其他错误
        logger.error(f"处理 translate_text 请求时发生未知错误: {str(e)}")
        return web.json_response({'code': -1, 'error': str(e)}, status=500)

    content = translate_text(params.text, params.target_language)
    logger.info("成功处理 translate_text 请求")
    return web.json_response({
        'code': 0, 
        'data': {
        'content': content,
        },
        'msg': 'translate_text',
    })


@routes.get('/merge_texts')
def merge_texts_route(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)
        # 记录请求日志
        logger.info(f"处理 merge_texts 请求: {request_data}")
        # 验证参数
        params = MergeTextRequest(**request_data)
    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        logger.error(f"参数验证失败: {error_message}")
        return web.json_response({'code': -1, 'error': error_message}, status=400)
    except Exception as e:
        # 其他错误
        logger.error(f"处理 merge_texts 请求时发生未知错误: {str(e)}")
        return web.json_response({'code': -1, 'error': str(e)}, status=500)

    content = merge_texts(params.text1, params.text2, params.language)
    logger.info("成功处理 merge_texts 请求")
    return web.json_response({
        'code': 0,
        'data': {
            'content': content,
        },
        'msg': 'merge_texts',
    })


def create_app():
    app = web.Application()
    app.add_routes(routes)
    return app