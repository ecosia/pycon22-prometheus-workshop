# Workshop: Monitoring Python Applications with Prometheus

## Objective

In the directory `app/`, we have a simple Python application. We want to start observing the behaviour of this application at runtime, by tracking and exporting metric data.

We will do this using the time-series database system [Prometheus](https://prometheus.io), which uses a "pull" method to extract data from running applications. This means that the applications need to "export" their data, so that Prometheus is able to "scrape" the metric data from them. This is typically done via an HTTP endpoint (`/metrics`, by convention).

We will use the [Prometheus Python client library](https://github.com/prometheus/client_python) to track metrics in our code.
