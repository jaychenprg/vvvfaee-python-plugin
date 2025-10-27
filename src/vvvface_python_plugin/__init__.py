from aiohttp import web

from .routes import create_openai_request_app

app = web.Application()

def create_app() -> web.Application:
    app = web.Application()
    app.add_subapp('/pyapi/vvv-face', create_openai_request_app())
    return app

def main() -> None:
    print("Hello from vvvface-python-plugin!")
    web.run_app(create_app(), host="localhost", port=8001)
