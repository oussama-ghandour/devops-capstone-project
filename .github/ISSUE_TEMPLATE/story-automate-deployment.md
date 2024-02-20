---
name: Story-automate-deployment
about: Create a CD pipeline to automate deployment to Kubernetes
title: ''
labels: enhancement
assignees: oussama-ghandour

---

Title: Create a CD pipeline to automate deployment to Kubernetes

**As a** developer
**I need** to create a CD pipeline to automate deployment to Kubernetes
**So that** the developers are not wasting their time doing it manually

### Assumptions
* Use Tekton to define the pipeline
* It should clone, lint, test, build, and deploy the service
* Deployment should be to OpenShift
* It can use a manual trigger for this MVP

### Acceptance Criteria
Given the CD pipeline has been created
When I trigger the pipeline run
Then I should see the accounts service deployed to OpenShift
