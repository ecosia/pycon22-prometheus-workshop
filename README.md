# Workshop: Monitoring Python Applications with Prometheus

## Objective

In the directory `app/`, we have a simple Python application. We want to start observing the behaviour of this application at runtime, by tracking and exporting metric data.

We will do this using the time-series database system [Prometheus](https://prometheus.io), which uses a "pull" method to extract data from running applications. This means that the applications need to "export" their data, so that Prometheus is able to "scrape" the metric data from them. This is typically done via an HTTP endpoint (`/metrics`, by convention).

We will use the [Prometheus Python client library](https://github.com/prometheus/client_python) to track metrics in our code.

## Prerequisites

For this workshop you will need [Python 3](https://installpython3.com/), [Pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv) and [Docker](https://docs.docker.com/get-docker/) running on your machine.

## Workshop Content

### Section 1: Exposing metrics

For this section, you can use `make dev` to install depencies and run the dev server.

To export our metrics we will need to have a server with a handler to handle the metrics. We can do this by changing the base class of our HTTPRequestHandler to the `MetricsHandler` provided by the prometheus python client. We also need to add the condition for the `/metrics` endpoint below our `/treecounter` endpoint condition.

``` python
class HTTPRequestHandler(MetricsHandler):
    ...
    ...
    elif endpoint == '/metrics':
        return super(HTTPRequestHandler, self).do_GET()
```

Now try restart the server (`control c` will stop it) and go to `localhost:8001/metrics` what do you see? What do you see if you visit `localhost:8001/treecounter` a few times and then go back to the `/metrics` endpoint?

### Section 2: Creating custom metrics

Now we are able to expose metrics we need to be able to create them. Prometheus has a few different data types, but the simplest is a `Counter` - this is a counter which always goes up, and can be used to track, for example, the number of requests received (you can then divide this unit over time to calculate requests per second). To create a `Counter`, import it from the Prometheus Python client and instanstiate it.

``` python
from prometheus_client import Counter
requestCounter = Counter('requests_total', 'decription of counter', ['status', 'endpoint']) # can be declared as a global variable
```

Then, you should be able to see your metric exposed on `/metrics` - success! (Except, it will still always report 0 - not quite useful, yet)

To use our metric in practice, we want to increment the counter when tracking events in our code. To increment the `Counter` type by one, we can simply call `.Inc()` - for example, using the request counter we created above, we could call:

``` python
requestCounter.labels(status='200', endpoint='/treecounter').inc()
```

**You should add these `.inc()` calls in the place in your code where the event you want to track is occuring.** If you want to increment by a different amount than 1 you can for example use `.inc(1.5)`.

Try add a counter to the application, add the labels which you find significant and a suitable name and description. See if when you run the server you can find it at `/metrics`. You may also want to experiment with the placement of you `.inc()` call.

### Section 3: Scraping Metrics with Prometheus

So far, we've been able to instrument our application, such that it is now exporting metrics about its runtime behaviour. However, we still need to collect those metrics and store the data in a way that we can query it back out, in order to graph it over time and make dashboards.

There is a `prometheus.yaml` configuration file here in the repo, which is already set up to scrape metrics from our application. We can run both our application and Prometheus inside Docker, so that they are easily able to find each other.

To build the application Docker image, and start the application container and Prometheus together, run the following command (from the root of this repo):

``` sh
docker-compose up --build
```

You should then be able to access the Prometheus dashboard on `http://localhost:9090`

Prometheus should find and immediately start scraping metrics from the application container. You can check that it's found the application container by looking at the list of "targets" that Prometheus is scraping `http://localhost:9090/targets`

### Section 4: Prometheus Queries

Prometheus using it's own query language called [PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/). You can enter PromQL queries in the `/graph` page of the Prometheus UI.

To see the counter exported previously, we can use the PromQL query:

``` sh
requests_total
```

If we want to see this graphed as a rate per-second over time, we use the query:

``` sh
rate(requests_total[1m])
```

### Section 5: Making Dashboards with Grafana

[Grafana](http://grafana.com) is an open-source metric visualisation tool, which can be used to create dashboards containing many graphs. Grafana can visualise data from multiple sources, including Prometheus. The `docker-compose` command used in the previous section will also start a Grafana container, which uses the Grafana configuration file in this repo to connect to Prometheus. After running the startup command (same as above, `docker-compose up --build`), you'll be able to find Grafana on `http://localhost:3000`

Grafana uses authentication, which, for this workshop, is configured in the `docker-compose.yaml` file. The credentials configured for this workshop are:

``` sh
username: ecosia
password: workshop
```
