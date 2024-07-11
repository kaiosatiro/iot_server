
**Receiver REST API**
This service is access by the various IOT devices access in order to send their status updates. The interface with the system, and the only service they’re aware about.

**Role**
To be lightweight and fast, its designed functionality is very focused and very minimal. The only task of the Receiver is to **receive** the message and push it into a queue.

**Stack**
A Web API interface, the devices are going to communicate via REST API.

- Python
- FastAPI with Uvicorn
- rabbitMQ with Pika
  
*The architecture:*
<div style="text-align: center;">
  <img src="/img/receiver_arch.png"/>
</div>

**Service Interface –** Exposes REST API for the devices. This layer receives the messages, and transfers them to the business logic layer.
**Business Logic –** Receives the messages from the Service Interface layer, makes sure the messages are valid, and passes them to the Queue Handler layer.
**Queue Handler –** The Queue handler receives the messages from the Business Logic layer, and adds them to the Queue.

***Logging* –** This is not an actual layer, but a cross-cutting component (accessible by all the layers). Contains the logging library that is being used by the service, and exposes a simple API to make the logging as simple and fast.

Every step in the service must be logged. Use the logging component generously.

No layer interferes with other layers, which will make the service more easy to maintain. By means of  dependency injection between the various layers. :syringe: 


---
