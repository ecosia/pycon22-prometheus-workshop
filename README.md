# Workshop: We know what your app did last summer. Do you? 👀
## Observing Python Applications with Prometheus 🔥🐍  

### Objective

In the directory `app/`, we have an application that runs a Python web server with the endpoint `/treecounter`. It displays the total number of trees planted by Ecosia users. We want to start observing the behavior of this application at runtime by tracking and exporting metric data.

We will do this using the time-series database system [Prometheus](https://prometheus.io), which uses a "pull" method to extract data from running applications. This means that the applications need to "export" their data, so that Prometheus is able to "scrape" the metric data from them. This is typically done via an HTTP endpoint (`/metrics`, by convention).

We will use the [Prometheus Python client library](https://github.com/prometheus/client_python) to track metrics in our code.

### Agenda

* [Section 1: Exposing metrics](#section-1:-exposing-metrics)
* [Section 2: Creating custom metrics](#section-2:-creating-custom-metrics)
* [Section 3: Scraping Metrics with Prometheus and creating Dashboards with Grafana](#section-3:-scraping-metrics-with-prometheus-and-creating-dashboards-with-grafana)
* [Bonus Material: Histograms in Prometheus](#bonus-material:-histograms-in-prometheus)

### Prerequisites

For this workshop you will need [Python 3.10](https://installpython3.com/), [Poetry](https://python-poetry.org/docs/#installation), [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) running on your machine. *(on mac os docker-compose is by default installed with Docker)*


Please note that this repository is linted using [black](), [flake8]() and [pycodestyle]() with a max line length of 100. This linting is enforced with github actions configured [here](./github/workflow/lint.yml)

## Workshop Content

---

### Section 1: Exposing metrics ⚙️

---

For this section, you can use the following command to install depencies and run the dev server locally.

```sh
# The Makefile allows us to run commands behind a target name
# Make is not available for the Windows OS so you will need to copy the commands from the Makefile and run them directly
make dev
```

To export our metrics we will need to have a server with a handler to *handle* the metrics. We can do this by changing the base class of our HTTPRequestHandler to the `MetricsHandler` provided by the prometheus python client. We also need to add the condition for the `/metrics` endpoint below our `/treecounter` endpoint condition. *(Don't forget to import the `MetricsHandler` from the `prometheus_client`)*

``` python
class HTTPRequestHandler(MetricsHandler):
    ...
    ...
    elif endpoint == '/metrics':
        return super(HTTPRequestHandler, self).do_GET()
```

Now try restarting the server (`control c` will stop it) and go to `localhost:8001/metrics`. What do you see? What do you see if you visit `localhost:8001/treecounter` a few times and then go back to the `/metrics` endpoint? What do these base metrics represent?

---

### Section 2: Creating custom metrics 🔧

---

Now that we can expose metrics, we need to create them. Prometheus has a few different data types but the most straight forward is a `Counter`. Counters always increment and can be used to track, for example, the number of requests received (you can then divide this unit over time to calculate requests per second). To create a `Counter`, import it from the Prometheus Python client and instantiate it.

``` python
from prometheus_client import Counter
requestCounter = Counter('requests_total', 'total number of requests', ['status', 'endpoint']) # can be declared as a global variable
```

Restart your server again and you should be able to see your metric exposed on `/metrics` - success! (Except, it will still always report 0 - not quite useful, yet)

```
# HELP requests_total Total requests
# TYPE requests_total counter
requests_total{} 0

```

To use our metric in practice, we want to increment the counter when tracking events in our code. To increment the `Counter` type by one, we can call `.inc()` - for example, using the request counter we created above, we could call:

``` python
requestCounter.labels(status='200', endpoint='/treecounter').inc()
```

**You should add these `.inc()` calls in the place in your code where the event you want to track is occurring.** If you want to increment by a different amount than 1, you can for example, use `.inc(1.5)`.

Add the call to `inc()` in your code. Try experiment with the placement of where you call it, what difference does it make to your metric?

---

### Section 3: Scraping Metrics with Prometheus and creating Dashboards with Grafana 🔥📈

---

So far we've been able to instrument our application, such that it is now exporting metrics about its runtime behavior. However, we still need to collect those metrics and store the data in a way so we can query it back out in order to graph it over time and make dashboards.

There is a `prometheus.yaml` configuration file here in the repo, which is already set up to scrape metrics from our application. We will run our application, Prometheus, and Grafana inside Docker, so that they are easily able to find each other.

#### Run the application, Prometheus and Grafana in Docker

To build the application Docker image and start the application container as well as Prometheus and Grafana together, run the following command (from the root of this repo):

``` sh
docker-compose up --build
```

*If you see errors it may be because you still have the previous version of the application running and therefore might be using the same port as you are now trying to access with Docker.*

You should then be able to access the Prometheus dashboard on `http://localhost:9090`

#### Navigating the Prometheus UI and using PromQL to query metrics

Prometheus should find and immediately start scraping metrics from the application container. You can check that it's found the application container by looking at the list of "targets" that Prometheus is scraping `http://localhost:9090/targets`

Prometheus uses it's own query language called [PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/). You can enter PromQL queries in the `/graph` page of the Prometheus UI.

To see the counter exported previously, we can use the PromQL query:

``` promql
requests_total
```

If we want to see this graphed as a rate per-second over time, we use the PromQL query:

``` promql
rate(requests_total[1m])
```

#### Making Dashboards with Grafana 

[Grafana](http://grafana.com) is an open-source metric visualization tool, which can be used to create dashboards containing many graphs. Grafana can visualize data from multiple sources, including Prometheus. The `docker-compose` command used in the previous section will also start a Grafana container, which uses the Grafana configuration file in this repo to connect to Prometheus. After running the startup command mentioned above, `docker-compose up --build`), you'll be able to find Grafana on `http://localhost:3000`

Grafana uses authentication, which, for this workshop, is configured in the `docker-compose.yaml` file. The credentials configured for this workshop are:

```
username: ecosia
password: workshop
```

Time to get creative and visualize your metrics in a meaningful way so you can observe your application and even set up alerts for any behavior you want to be informed about! We will show you in the workshop how to build a simple dashboard panel but there's lots to explore. Lots of useful information can be found on both the [Prometheus](https://prometheus.io) and [Grafana](http://grafana.com) websites.

✨ **Go forth and Monitor!!** ✨

---

### Bonus Material: Histograms in Prometheus 📊

---

We likely will not get to this material due to the workshop length, however for those of you who want to continue we created this section with some additional challenges and information to further support you in monitoring your applications.

We have already exposed metrics of type `Counter`. [Prometheus has four core metrics](https://prometheus.io/docs/concepts/metric_types/), which are:

 - Counter
 - Gauge
 - Histogram
 - Summary

A histogram is a little bit more complicated than a Counter, but it can be very useful!

For example a histogram is useful when you want approximations over a known range of values, such as:
* response duration
* request size

In Prometheus, a histogram measures the frequency of value observations that fall into `buckets`.
For example, we can define a set of buckets to measure request latency. These buckets are groupings which we can use to provide an indication of how long
a single request could take e.g. 0.0 - 0.25s, 0.25 - 0.50s, 0.50 - 0.75s, 0.75 - 1.00s, 1.00s+. The duration of every request will fall into one of these buckets.

In Prometheus, a histogram is cumulative and there are default buckets defined, so you don't need to specify them for yourself.
When using the histogram, Prometheus won't store the exact request duration, but instead stores the frequency of requests that fall into these buckets.

**Let's make a histogram for request latencies**

The first thing we will do is add the import:

```
  from prometheus_client import Histogram
```

Then define our histogram:

```
  requestHistogram = Histogram('request_latency_seconds', 'Request latency', ['endpoint'] )
  requestHistogramTreeCounter = requestHistogram.labels(endpoint='/treecounter')
```

Finally we add the following decorator to the piece of code that we want to measure the duration for:

```
  @requestHistogramTreeCounter.time()
  def xxxx():
      ...
```

Now restart the application and make a few requests. 👀

#### How to interpret the histogram 

If we curl the `/metrics` endpoint again, a portion of the output will look something like this:

```
request_latency_seconds_count{endpoint="/treecounter"} 5.0
```

This is a `count` again! And we can see the endpoint has received 5 requests. 

We also see our buckets. Here `le` means `less than or equal to`.
We can see from this output that the histogram is cumulative:

```
request_latency_seconds_bucket{endpoint="/treecounter",le="0.005"} 1.0
request_latency_seconds_bucket{endpoint="/treecounter",le="0.01"} 1.0
request_latency_seconds_bucket{endpoint="/treecounter",le="0.025"} 1.0
request_latency_seconds_bucket{endpoint="/treecounter",le="0.05"} 1.0
request_latency_seconds_bucket{endpoint="/treecounter",le="0.075"} 1.0
request_latency_seconds_bucket{endpoint="/treecounter",le="0.1"} 1.0
request_latency_seconds_bucket{endpoint="/treecounter",le="0.25"} 4.0
request_latency_seconds_bucket{endpoint="/treecounter",le="0.5"} 4.0
request_latency_seconds_bucket{endpoint="/treecounter",le="0.75"} 5.0
request_latency_seconds_bucket{endpoint="/treecounter",le="1.0"} 5.0
request_latency_seconds_bucket{endpoint="/treecounter",le="2.5"} 5.0
request_latency_seconds_bucket{endpoint="/treecounter",le="5.0"} 5.0
request_latency_seconds_bucket{endpoint="/treecounter",le="7.5"} 5.0
request_latency_seconds_bucket{endpoint="/treecounter",le="10.0"} 5.0
request_latency_seconds_bucket{endpoint="/treecounter",le="+Inf"} 5.0
```

Finally we see the total sum of all observed values:

```
request_latency_seconds_sum{endpoint="/treecounter"} 1.13912788000016
```

To learn more, you can read about [Prometheus Histogram best practices](https://prometheus.io/docs/practices/histograms/).

---

## Troubleshooting

### Port conflict

If you see the error message below it is likely because you already have either the Docker version or non docker version of the application already running.

```
Error starting userland proxy: listen tcp4 0.0.0.0:8001: bind: address already in use
```

Check you terminal windows to see if you can find where it is running and use `ctrl c` to stop it. Alternatively you can use `lsof -i :8001` to find out the `pid` of the process running at this port and `kill <pid-number>` to stop it. You may have to run these commands as `sudo`.

### Python version

If the App will not start locally and you receive an error referring the version, it may be because you do not have a suitable version of Python available on your machine. The version should be 3.10 or above.

---

The latest version of this material has been developed by @vinesse @sleepypioneer with previous iterations supported by @emilywoods @jasongwartz.