---
name: story-cd-pipeline
about: Create a CD pipeline to automate deployment to Kubernetes
title: ''
labels: technical debt
assignees: oussama-ghandour

---

Title: Containerize your microservice using Docker

**As a** developer
**I need** to containerize my microservice using Docker
**So that** I can deploy it easily with all of its dependencies

### Assumptions
* Create a `Dockerfile` for repeatable builds
* Use a `Python:3.9-slim` image as the base
* It must install all of the Python requirements
* It should not run as `root`
* It should use the `gunicorn` wsgi server as an entry point

### Acceptance Criteria
Given the Docker image named accounts has been created
When I use `docker run accounts`
Then I should see the accounts service running in Docker
