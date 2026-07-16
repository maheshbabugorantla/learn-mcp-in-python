"""Two bits of ASGI plumbing, given to you so you can spend your time on auth.

You never edit this file, but do read it — `app.py` is built out of these two
and they'll make more sense than they will as magic.

An ASGI middleware is a thing that wraps an app and gets called first. It can
answer the request itself, or pass it down. That's the whole idea; both classes
here are ten lines of it.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class WithCors:
    """Add CORS headers to responses, for requests you say need them.

    `get_cors_headers(request)` returns a dict of headers to add, or `None` to
    leave the response alone. Preflight `OPTIONS` requests are answered here
    and never reach the app underneath.
    """

    def __init__(
        self,
        app: ASGIApp,
        get_cors_headers: Callable[[Request], Mapping[str, str] | None],
    ) -> None:
        self.app = app
        self.get_cors_headers = get_cors_headers

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = self.get_cors_headers(Request(scope))
        if not headers:
            await self.app(scope, receive, send)
            return

        if scope["method"] == "OPTIONS":
            preflight = Response(
                status_code=204,
                headers={**dict(headers), "Access-Control-Max-Age": "86400"},
            )
            await preflight(scope, receive, send)
            return

        async def send_with_cors(message: Message) -> None:
            # Headers have to go on as the response starts, and they go on
            # *every* response — including the 401s and 404s. A browser that
            # can't read an error response is a browser that can't tell you
            # what went wrong.
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                for key, value in headers.items():
                    response_headers[key] = value
            await send(message)

        await self.app(scope, receive, send_with_cors)


class WithAuth:
    """Run an `authorize` check before the app sees the request.

    `authorize(request)` returns a `Response` to reject the request, or `None`
    to let it through. This is where your 401s and 403s come from.
    """

    def __init__(
        self,
        app: ASGIApp,
        authorize: Callable[[Request], Awaitable[Response | None]],
    ) -> None:
        self.app = app
        self.authorize = authorize

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        rejection = await self.authorize(Request(scope))
        if rejection is not None:
            await rejection(scope, receive, send)
            return

        await self.app(scope, receive, send)
