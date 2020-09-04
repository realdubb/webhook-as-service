### Process POST
1. Receive a POST request with information on the webhook the service should send (headers, request type,
        POST body, URL params, etc)
2. Have Request Class
3. Store Request in RequestDB with appropriate status
      - Return accepted status with URL with Id for location to ping to get status
      - Process Requests in RequestDB in background
      - Update Accordingly
4. Implement retry logic for bad status code with an exponential backoff if the webhook URL responds with a bad status code (non-200)

### Process GET
 1. GET status/id endpoint that shows the status of the webhook sent
 2. Get Request by Id from RequestDB
