from flask import Flask, request, Response
from webhook_processor import WebhookProcessor

app = Flask(__name__)

webhook_processor = WebhookProcessor()
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

@app.route('/')
def status():
    return 'All things go!'


@app.route('/current-state', methods=["GET"])
def current_state():
    return webhook_processor.get_db_state()


@app.route('/webhook', methods=["POST"])
def post_webhook():
    if request.method == 'POST':
        content = request.get_json()
        try:
            request_id = webhook_processor.queue_request(content)
        except KeyError as e:
            resp = Response(response=f"Missing required parameters {str(e.args)}")
            resp.status_code = 400
            return resp
        location_url = request.host_url + 'webhook/' + str(request_id)
        resp = Response("{ ""id"": %s }" % request_id)
        resp.status_code = 202
        resp.headers.add('Location', location_url)
        return resp


@app.route('/webhook/<int:request_id>', methods=["GET"])
def get_webhook(request_id):
    try:
        return webhook_processor.get_request_status(request_id)
    except KeyError:
        resp = Response("Invalid id given: %s" % request_id)
        resp.status_code = 404
        return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    webhook_processor.run()
