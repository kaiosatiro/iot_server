# IoT Telemetry Application
[![Tests](https://github.com/kaiosatiro/iot_server/actions/workflows/deploy-staging.yml/badge.svg)](https://github.com/kaiosatiro/iot_server/actions/workflows/deploy-staging.yml)
[![QA](https://github.com/kaiosatiro/iot_server/actions/workflows/qa.yml/badge.svg)](https://github.com/kaiosatiro/iot_server/actions/workflows/qa.yml)

:construction: In progress ... :construction:

IoT stands for Internet of Things and represents small, always-connected devices. Smart Homes are a great example of IOT consumers. The typical smart home has a lot of IOT devices such as thermostats, lightbulbs, cameras, electric switches, and lots more. 

The purpose of this project is to put into practice many concepts that I've been learning about system architecture and development, and others that I need to.

Whether developing a home automation system, industrial monitoring solution, or experimenting with IoT concepts, this server may provide a scalable and flexible foundation.

#### Demo: 
**Docs:** [https://staging.iotserverapp.com/userapi/v1/docs](https://staging.iotserverapp.com/userapi/v1/docs)

**Admin Panel:** [https://staging.iotserverapp.com/admin](https://staging.iotserverapp.com/admin) (admin:admin)

**User Dashboard:** https://dashboard.iotserverapp.com/  -- *In development* 

#### Technology Stack and Features

- ⚡ [FastAPI](https://fastapi.tiangolo.com/) for the Python backend API.
  - 💾 [PostgreSQL](https://www.postgresql.org/) as the SQL database.
  - 🔍 [Pydantic](https://docs.pydantic.dev/latest/), used by FastAPI, for the data validation and settings management.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com/) for the Python SQL database interactions (ORM).
  - 🛠️ [Alembic](https://alembic.sqlalchemy.org/) for database migrations.
- 🐇 [rabbitMQ](https://www.rabbitmq.com/) for message queueing
  - 📬 [pika](https://pika.readthedocs.io/en/stable/) for python integration
- 🐋 [Docker Compose](https://www.docker.com/) for development and production.
- 🔗 Correlation ID shared between the services for tracking
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://docs.pytest.org/en/stable/).
- 📞 [Nginx](https://nginx.org/en/) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on [GitHub Actions](https://docs.github.com/en/actions) on a [EC2 AWS](https://aws.amazon.com/pt/ec2/) instance.

**Intended to practice:**
- 📐 SOA (Service-Oriented Architecture)
- ✅ TDD (Test-Driven Development)
- 📝 Low level design documentation (in progress)
- 🏗️ Design Patterns (like Dependency Injection, Singleton, etc)
- 🏭 CI/CD.
- 🚀 Full-Stack Development (Mostly backend engeering on this repo)
- :arrow_up: Scalability: Services can be independently scalable.
- 📦 Statelessness: Services should be stateless to ensure easy scaling and resilience.
- 🧱 Reliability: Ensure data integrity and system reliability
- And more...

---

#### Run Locally
Needs Docker Compose

- Clone the project
- Create a `.env` file in the root directory with all the environment variables present in the `.env.example` file. (Can change it, but it is ready to go)

At the project root directory:
```bash
#with make
make compose-dev-d
#with only dokcer-compose
docker compose -f docker-compose.yml -f docker-compose-override.yml up --build -d
```
Access the API DOC at `http://localhost:8000/docs` and the Admin Panel at `http://localhost:8000/admin` (admin:admin)

**This will run a development environment with the API services containers binded to the repo folder, so you can edit the code and see the changes in real-time.*

Then: 
- Create a **User** on the admin panel or the swagger interactive docs
- Create a **Site** ('Site' in the sense of a location, like a house, a factory, etc)
- Create a **Device** and use its token to send a POST request to `http://localhost:8100/` with JSON data


```bash
# Follow the local log activity on the /logs folder
cd /logs
tail -f <FILE>
```


```bash
# stopping cleaning the volumes
make compose-down-dev
```

---
### Documentation
:construction: In progress ... :construction:
#### Requirements
**Functional Requirements**
1. Receive status updates from IOT devices
2. Store the updates for future use
3. Allow end users to vizualize data through a dashboard

**\*Fictional Non-Functional Requirements\***
1. Data Volume: 54GB Annually
2. Load: 500 concurrent requests
3. No. of users: 1,000,000
4. Message loss: 1%
5. SLA: Very high

### Overall Architecture
Here is the architecture diagram:

<div style="text-align: center;">
  <img src="/doc/logic_diagram.png" alt="Alt text" />
</div>

#### Services

- **Logging**: Aggregates logs from various services, pulling them from a queue handling them organized on local files or/and foward them to a cloud service.

- **Receiver**: Receives status updates from devices by an exposed **REST API** and adds them to a queue for further handling.
- **Handler**: Validates and parses the updates, converting them to a unified format per device on the DB.
- **User API**: Exposes an API for users to signup, create Sites and Devices, and access the data stored on the DB. 
- ------
- **Dashboard**: A web interface for users. (Still working on this on a separate repo)
---
#### ✨ Inspirations
- [FastAPI FullStackTemplate](https://github.com/fastapi/full-stack-fastapi-template)
-  [Memi Lavi Courses](https://www.linkedin.com/in/memilavi/)
-  [Hussein Nasser Courses](https://www.linkedin.com/in/hnaser/)


🌐🚀