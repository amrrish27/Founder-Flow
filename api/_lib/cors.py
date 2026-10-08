"""
Shared CORS helper for all Vercel serverless functions.
"""


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


def handle_options(handler_instance):
    handler_instance.send_response(200)
    for k, v in cors_headers().items():
        handler_instance.send_header(k, v)
    handler_instance.end_headers()
