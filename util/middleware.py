from flask import Request, g, Response, json

from util.rate_limit import RateLimit


class RateLimitingMiddleware:
    """
    Simple WSGI middleware
    """

    def __init__(self, app, limit, per, send_x_headers=True, over_limit=RateLimit.on_over_limit):
        self.app = app
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        self.over_limit = over_limit

    def __call__(self, environ, start_response):
        """
        middleware to capture request header from incoming http request
        """
        request = Request(environ)
        over_limit = self.over_limit
        per = self.per
        limit = self.limit
        send_x_headers = self.send_x_headers

        key = "rate-limit:{}:{}".format(request.remote_addr, request.path)
        r_limit = RateLimit(key_prefix=key, limit=limit, per=per, send_x_headers=send_x_headers)

        def new_start_response(status, response_headers, exc_info=None):
            """
            set custom response headers
            """
            # set the request header as response header
            g._view_rate_limit = r_limit
            if r_limit and r_limit.send_headers:
                response_headers.append(('X-RateLimit-Limit', str(r_limit.limit)))
                response_headers.append(('X-RateLimit-Remaining', str(r_limit.remaining)))
                response_headers.append(('X-RateLimit-Reset', str(r_limit.reset)))

            return start_response(status, response_headers, exc_info)

        if over_limit and r_limit.over_limit:
            res = Response(json.dumps({
                    "error": "403",
                    "data": "Too many requests, You hit the rate limit"
                }), content_type="application/json", status=403)
            return res(environ, start_response)

        return self.app(environ, new_start_response)
