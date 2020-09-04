import threading
import time
import datetime

from flask import jsonify
from requests import Response, post, get, put
from webhook_request import WebhookRequest


class WebhookProcessor(object):
    """
        Class that will process webhooks in the background. Queueing, executing and reporting on the status.
        The run() method will be started and it will run in the background
        until the application exits.
    """

    def __init__(self, interval=5):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.request_queue = []
        self.request_db = {}

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        """ Processes queue of webhook requests, removing requests when completed
            or canceled by exceeding retry threshold
            Runs for the lifetime of application in interval defined in constructor
        """
        while True:
            completed_requests = []
            canceled_requests = []
            for request_id in self.request_queue:
                request = self.request_db[request_id]
                if request.request_time < datetime.datetime.now() and request.request_status != 'canceled':
                    response = self.process_request(request)
                    if response.status_code == 200:
                        completed_requests.append(request_id)

                elif request.request_status == 'canceled':
                    canceled_requests.append(request)

            # Remove requests that have been completed from queue
            requests_to_remove = set(completed_requests) | set(canceled_requests)
            self.request_queue = list(set(self.request_queue) - requests_to_remove)
            time.sleep(self.interval)

    def get_db_state(self):
        """
        Gets representation of current state of the database
        :return: Json
        """
        json_dict = {'pending_requests': [], 'current_state': []}

        for request_id in self.request_queue:
            json_dict['pending_requests'].append({'id': request_id})

        for request_id in self.request_db:
            request = self.request_db[request_id]
            json_dict['current_state'].append(request.to_dict)

        return jsonify(json_dict)

    def get_request_status(self, request_id: str):
        """
        Gets status of request from in memory database given id
        :param request_id:
        :return: string: status of the webhook request
        """
        request = self.request_db[request_id]
        return request.request_status

    def queue_request(self, json_data):
        """
        Adds webhook request to queue to be processed and persists the request in-memory db
        :param json_data:
        :return: id: int - unique id of the request
        """
        request = WebhookRequest(json_data)
        self.request_queue.append(request.id)
        self.request_db[request.id] = request
        return request.id

    @staticmethod
    def process_request(webhook_request: WebhookRequest):
        """
        Takes a webhook requests and executes the http request and sets it's completion/retry status based on response
        :param webhook_request:
        :return: Response
        """
        body = webhook_request.body
        headers = webhook_request.headers
        url = webhook_request.url
        params = webhook_request.query_params
        response: Response = Response()

        webhook_request.request_attempts = webhook_request.request_attempts + 1
        webhook_request.request_status = 'processing'

        if webhook_request.request_type == 'POST':
            response = post(url, json=body, headers=headers, params=params)
        elif webhook_request.request_type == 'PUT':
            response = put(url, json=body, headers=headers, params=params)
        elif webhook_request.request_type == 'GET':
            response = get(url, json=body, headers=headers, params=params)

        if response.status_code == 200:
            webhook_request.request_status = 'complete'
        else:
            next_attempt_at = WebhookProcessor.schedule_next_attempt(webhook_request.request_attempts,
                                                                     webhook_request.request_time)
            # Cancel request if next scheduled attempt is more than 24hrs from now, else retry
            if next_attempt_at > datetime.datetime.now() + datetime.timedelta(hours=24):
                webhook_request.request_status = 'canceled'
                webhook_request.request_time = datetime.datetime.max
            else:
                webhook_request.request_status = 'retrying'
                webhook_request.request_time = next_attempt_at

        return response

    @staticmethod
    def schedule_next_attempt(attempts: int, last_attempt: datetime) -> datetime:
        """
            Schedules next time request should be retried, exponentially backing off the time
            given the number of tries.
            2^attempts + 60*attempts
            1 = 62 seconds
            2 = 124 seconds
            3 = 188 seconds
            ...
            16 = 66,496 seconds ~18hrs, is maximum backoff
        """
        seconds_until_next_try = pow(2, attempts) + (60 * attempts)
        return last_attempt + datetime.timedelta(seconds=seconds_until_next_try)
