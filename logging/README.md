
**Logging service**
Aggregates logs from various services, pulling them from a queue:


**Role**
The logging service is the aggregator of all the logs generated by the other system’s services.
All the other services write their logs to a queue, and the logging service polls them, and stores them in a central data store. This way, we are able to get a unified view of all the events that happened in the system and are not required to go through different log files, in different formats, just to get a coherent view of a specific flow or error.

**Stack**
Because the logging service is an always-active service and does not wait for requests in order to return a response, it is going to be a Python service that consumes from a RabbitMQ Queue.

Here is the architecture with a description of every layer:

<div style="text-align: center;">
  <img src="/img/logging_arch.png"/>
  <img src="/img/logging_service_flow.png"/>
</div>

No layer interferes with other layers, which will make the service more easy to maintain.

:syringe: By means of  dependency injection between the various layers.


---