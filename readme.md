# TaskPulse

## Requirement

To design a FastAPI app, which has an API which accepts requests to process a long-running program, but the API should
respond back immediately after receiving the request, without waiting for the long-running program to be completed, and
there should be another websocket or API, which the client can use to get the progress of the task in percentages, how
would you design it. Consider that the API might receive thousands of requests at a time, and the APIs should scale
perfectly without freezing or crashing. So, using in-memory objects is not recommended.

Designing a FastAPI app to handle long-running tasks efficiently while providing immediate responses and progress
updates involves several components. Here's a high-level design approach:

### 1. **Task Queue and Worker System**

- **Celery**: Use Celery to handle the long-running tasks. Celery is a distributed task queue that can manage task
  execution asynchronously.
- **Message Broker**: Use RabbitMQ or Redis as the message broker for Celery to handle task distribution.

### 2. **FastAPI for Immediate Response**

- **API Endpoint**: Create an endpoint that accepts the request and immediately returns a task ID.
- **Task Submission**: When a request is received, submit the task to Celery and return the task ID to the client.

### 3. **Progress Tracking**

- **Backend Storage**: Use a database (e.g., PostgreSQL) to store task progress and status. This avoids using in-memory
  objects and ensures scalability. Here in this sample program, sqllite db is used for simplicity.
- **Task Updates**: The worker updates the task progress in the database.

### 4. **WebSocket for Real-Time Updates**

- **WebSocket Endpoint**: Create a WebSocket endpoint in FastAPI that clients can connect to for real-time progress
  updates.
- **Progress Notifications**: Use a Pub/Sub mechanism (e.g., Redis Pub/Sub) to notify the WebSocket server of progress
  updates, which then pushes updates to the connected clients.

### 5. **API for Polling Progress**

- **Progress Endpoint**: Create an API endpoint that clients can poll to get the current progress of a task using the
  task ID.

### 6. **Scalability Considerations**

- **Load Balancer**: Use a load balancer (e.g., Nginx) to distribute incoming requests across multiple instances of the
  FastAPI app.
- **Horizontal Scaling**: Deploy multiple instances of the FastAPI app and Celery workers to handle high loads.
- **Database Optimization**: Ensure the database is optimized for high read/write operations, possibly using indexing
  and partitioning.

### Conclusion

This design ensures that the FastAPI app can handle a high volume of requests without freezing or crashing, by
offloading long-running tasks to Celery and using a database for progress tracking. The WebSocket endpoint provides
real-time updates, while the API endpoint allows for polling progress.