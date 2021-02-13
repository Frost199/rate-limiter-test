from flask import Flask, jsonify, Response
from util.decorators import rate_limit
from util.rate_limit import RateLimit

app = Flask(__name__)


@app.after_request
def inject_x_rate_headers(response: Response) -> 'Response':
    limit: RateLimit = RateLimit.get_view_rate_limit()
    if limit and limit.send_headers:
        header = response.headers
        header.add('X-RateLimit-Limit', str(limit.limit))
        header.add('X-RateLimit-Remaining', str(limit.remaining))
        header.add('X-RateLimit-Reset', str(limit.reset))
    return response


@app.route('/', methods=['GET'])
@rate_limit(limit=4, per=30, send_x_headers=True)
def page_one():
    return jsonify({
        "success": "200",
        "data": "Hello User"
    }), 200


@app.route('/second-page', methods=['GET'])
@rate_limit(limit=4, per=30, send_x_headers=True)
def page_two():
    return jsonify({
        "success": "200",
        "data": "Hello User, Welcome to page 2"
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
