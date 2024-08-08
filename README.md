# IoT Telemetry Application
![Test](https://github.com/kaiosatiro/iot_server/actions/workflows/test.yml/badge.svg)
![QA](https://github.com/kaiosatiro/iot_server/actions/workflows/qa.yml/badge.svg)


:construction: In progress ... :construction:

IoT stands for Internet of Things and represents small, always-connected devices. Smart Homes are a great example of IOT consumers. The typical smart home has a lot of IOT devices such as thermostats, lightbulbs, cameras, electric switches, and lots more. 

The purpose of this project is to put into practice many concepts that I've been learning about system architecture and development, and others that I need to.

Whether developing a home automation system, industrial monitoring solution, or experimenting with IoT concepts, this server may provide a scalable and flexible foundation.

#### Technology Stack and Features

- ⚡ FastAPI for the Python backend API.
  - 💾 PostgreSQL as the SQL database.
- 🐋 Docker Compose for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- ✅ Tests with Pytest.
- 📞 Traefik as a reverse proxy / load balancer.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

- :arrow_up: Scalability: Services can be independently scalable.
- 📦 Statelessness: Services should be stateless to ensure easy scaling and resilience.
- 🧱 Reliability: Ensure data integrity and system reliability

---

## Documentation
:construction: In progress ... :construction:

#### Requirements
**Functional Requirements**
1. Receive status updates from IOT devices
2. Store the updates for future use
3. Allow end users to vizualize data through a dashboard

**\*Fictional Non-Functional Requirements\***
1. Data Volume: 54GB Annually
2. Load: 540 concurrent requests
3. No. of users: 2,000,000
4. Message loss: 1%
5. SLA: Very high

### Overall Architecture
Here is the architecture diagram:

<div style="text-align: center;">
  <img src="/doc/logic_diagram.png" alt="Alt text" />
</div>

#### Services

-- **Logging**: Aggregates logs from various services, pulling them from a queue:

<div style="text-align: center;">
  <img src="/doc/logging_arch.png" alt="Alt text" />
</div>


- **Receiver**: Receives status updates from devices by an exposed **REST API** and adds them to a queue for further handling.
- **Handler**: Validates and parses the updates, converting them to a unified format.
- **Dash Board**: WepApp with a Dashboard for data vizualization.

---

🌐🚀