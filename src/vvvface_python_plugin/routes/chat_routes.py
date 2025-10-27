from copyreg import constructor

from aiohttp import web
from pydantic import ValidationError

from ..schemas import AnalyzeImageRequest, ImageToVideoRequest, TextToVideoRequest, TranslateTextRequest
from ..utils import analyze_image_prompt, image_to_video_prompt, text_to_video_prompt, translate_text

routes = web.RouteTableDef()

@routes.get('/analyze_image')
def analyze_image(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)
        # 验证参数
        params = AnalyzeImageRequest(**request_data)
    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        return web.json_response({'error': error_message}, status=400)
    except Exception as e:
        # 其他错误
        return web.json_response({'error': str(e)}, status=500)

    # 处理请求
    content = analyze_image_prompt(params.image_url, params.language)

    # 返回结果
    return web.json_response({
        'message': 'analyze_image',
        'content': content,
    })

@routes.get('/image_to_video')
def image_to_video(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)

        # 验证参数
        params = ImageToVideoRequest(**request_data)
    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        return web.json_response({'error': error_message}, status=400)
    except Exception as e:
        # 其他错误
        return web.json_response({'error': str(e)}, status=500)

    content = image_to_video_prompt(params.image_url, params.language)
    return web.json_response({
        'message': 'image_to_video',
        'content': content,
    })

@routes.get('/text_to_video')
def text_to_video(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)

        # 验证参数
        params = TextToVideoRequest(**request_data)
    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        return web.json_response({'error': error_message}, status=400)
    except Exception as e:
        # 其他错误
        return web.json_response({'error': str(e)}, status=500)

    content = text_to_video_prompt(params.language)
    return web.json_response({
        'message': 'text_to_video',
        'content': content,
    })

@routes.get('/translate_text')
def translate_text(request):
    try:
        # 获取参数
        request_data = dict(request.rel_url.query)

        # 验证参数
        params = TranslateTextRequest(**request_data)

    except ValidationError as e:
        # 参数验证失败
        error_message = ', '.join([err['msg'] for err in e.errors()])
        return web.json_response({'error': error_message}, status=400)
    except Exception as e:
        # 其他错误
        return web.json_response({'error': str(e)}, status=500)

    content = translate_text(params.text, params.target_language)
    return web.json_response({
        'message': 'translate_text',
        'content': content,
    })

def create_app():
    app = web.Application()
    app.add_routes(routes)
    return app
