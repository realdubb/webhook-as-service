from datetime import datetime


class WebhookRequest:
    """
        Model of a webhook request. Class variable id is incremented with each new request created
    """
    id = 0

    def __init__(self, json_data):
        self.url = json_data['url']
        self.headers = json_data['headers']
        self.request_type = json_data['requestType']
        self.query_params = None
        self.body = json_data['body']
        self.request_status = 'created'
        self.request_time = datetime.now()
        self.request_attempts = 0

        if 'queryParams' in json_data:
            self.query_params = json_data['queryParams']

        WebhookRequest.id = WebhookRequest.id + 1
        self.id = WebhookRequest.id

    @property
    def to_dict(self):
        """
        Converts object to dictionary for representation in JSON
        :return: dictionary
        """
        json_dict = {
            'id': self.id,
            'url': self.url,
            'headers': self.headers,
            'request_type': self.request_type,
            'request_attempts': self.request_attempts,
            'request_status': self.request_status,
            'request_body': self.body
        }

        if self.query_params is not None:
            json_dict['query_params'] = self.query_params

        if self.request_status == 'complete':
            json_dict['completed_at'] = self.request_time.isoformat()
        elif self.request_status == 'retrying':
            json_dict['next_attempt_at'] = self.request_time.isoformat()
        else:
            json_dict['request_created_at'] = self.request_time.isoformat()

        return json_dict
