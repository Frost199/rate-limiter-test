from functools import wraps, update_wrapper

from flask import request, g, Response

from util.rate_limit import RateLimit


def rate_limit(limit=50, per=3600, send_x_headers=True, over_limit=RateLimit.on_over_limit,
               scope_function=lambda: request.remote_addr, key_function=lambda: request.endpoint):

    def rate_limit_decorator(f):

        @wraps(f)
        def rate_limited(*args, **kwargs):

            key = "rate-limit:{}:{}".format(key_function(), scope_function())
            r_limit = RateLimit(key_prefix=key, limit=limit, per=per, send_x_headers=send_x_headers)
            g._view_rate_limit = r_limit
            if r_limit and r_limit.send_headers:
                resp = Response()
                resp.headers.add('X-RateLimit-Limit', str(r_limit.limit))
                resp.headers.add('X-RateLimit-Remaining', str(r_limit.remaining))
                resp.headers.add('X-RateLimit-Reset', str(r_limit.reset))
            if over_limit and r_limit.over_limit:
                return over_limit(r_limit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return rate_limit_decorator
