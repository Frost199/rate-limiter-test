from typing import Callable, Tuple, Union, Dict
import time

from flask import g, jsonify
from redis import Redis

redis = Redis(host='redis', port=6379, decode_responses=True)


class RateLimit:
    """
    A Rate limiting class
    """
    # this will give my key an extra 10 seconds to expire in redis, so that badly
    # synchronized clocks between workers and the redis server do not cause problems
    expiration_window = 5

    def __init__(self, key_prefix: str = 'rl', limit: int = 40, per: int = 60, send_x_headers: bool = True):
        """
        Rate limiting initialization values
        Args:
            key_prefix: A key prefix to be added to the redis cache,
                        used to keep track of the rate limit from each of the request.
            limit: number of request to be allowed over a time period
            per: period for this request to be allowed
            send_x_headers: a  boolean option that will allow us inject each response header,
                            the number of allowed requests and remaining requests
        """

        # reset has to be in int, to achieve this, get the current time in seconds since the epoch,
        # this is a floating value, divide by the per e.g 60 seconds and make it an int by casting to an int.
        # multiply it back with the per you used to divide, this returns the current time in int,
        # then add the current time to the per, as this will set the time it should reset after
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + self.reset.__str__()
        self.limit = limit
        self.per = per
        self.send_headers = send_x_headers

        pipeline = redis.pipeline()
        pipeline.incr(self.key)
        pipeline.expireat(self.key, self.reset + self.expiration_window)
        self.current = pipeline.execute()[0]

    @property
    def remaining(self) -> int:
        """
        This calculates how many request are left
        Returns:
            The number fo request left
        """
        remaining_request: Callable[['RateLimit'], int] = lambda \
            x: 0 if x.limit - x.current <= 0 else x.limit - x.current
        return remaining_request(self)

    @property
    def over_limit(self) -> bool:
        check_over_limit: Callable[['RateLimit'], bool] = lambda x: x.current > x.limit
        return check_over_limit(self)

    @staticmethod
    def get_view_rate_limit() -> 'RateLimit':
        return getattr(g, '_view_rate_limit', None)

    @staticmethod
    def on_over_limit(limit: 'RateLimit') -> Union[Tuple[Dict[str, str], int], None]:
        if limit.over_limit:
            return jsonify(
                {
                    "error": "403",
                    "data": "Too many requests, You hit the rate limit"
                },
            ), 403
        return None
