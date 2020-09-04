# Webhook as a Service

Found on docker - latest build from master branch
 
 `docker pull realdubb/webhook-as-service:latest`

### Requirements
 - Git
 - Docker
 
### Quick Start
1. Clone and `cd` into repo
2. Build and run docker image `docker-compose up`
3. Hit exposed endpoint `http://localhost:5000`, port can be changed in `docker-compose.yml`


### File Structure
 - `app.py` - http routing and main entry point
 - `webhook_processor.py` - app logic for persisting and processing webhooks
 - `webhook_request.py` - class to represent webhook

### API Docs

#### `GET /` 
To let you know service is running.
 - returns `200` `All things go!`
 
#### `GET /current-state` 
To let you know current status of requests
 - returns `200` with JSON of current_state of database, and pending_requests
```js
{
    "current_state": [
        {
            "completed_at": "2020-09-03T12:59:28.201452",
            "headers": {
                "Content-Type": "application/json"
            },
            "id": 1,
            "query_params": {
                "q": "masquerade shirt"
            },
            "request_attempts": 1,
            "request_body": "{\"color\": \"green\", \"size\":\"large\"}",
            "request_status": "complete",
            "request_type": "GET",
            "url": "https://webhook.site/283155b9-60cc-4621-a2cc-ac72e5ba4151"
        }
    ],
    "pending_requests": [{ "id": "int" }]
}
```

#### `GET /webhook/{id}`
 - Accepts `id` as int
 - Returns `200` with `created`, `processing`, `complete`, `retrying`, `canceled`
    
#### `POST /webhook`
 - Accepts `application/json` in body
    
 Example of valid request
 
```js
{
    "url": "https://webhook.site/283155b9-60cc-4621-a2cc-ac72e5ba4151",
    "requestType": "GET", 
    "queryParams": {
        "q": "masquerade shirt"
    },
    "headers": {
        "Content-Type": "application/json"
    },
    "body": "{\"color\": \"green\", \"size\":\"large\"}"
}
```
  
- Required json params
    - url: valid url
    - requestType: `GET`, `PUT` or `POST`
    - headers: object with key/values of HTTP Headers
    - body: string to send to webhook
- Optional json keys
    - queryParams: object with key/values of HTTP Query Parameters
- Returns `202` with `created`, `processing`, `complete`, `retrying`, `canceled`
    - Location header will contain url, to GET webhook status
- Returns `400` if any required params are missing