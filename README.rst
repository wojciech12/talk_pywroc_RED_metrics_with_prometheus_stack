=========================================================================
RED metrics for a REST service with Prometheus, AlertManager, and Grafana
=========================================================================

How to monitor your micro-service with Prometheus? How to design metrics, what is USE and RED?

Presentation and live-coding demo:

- slides/ - check `the pdf export <slides/index.pdf>`_
- src/ - an example REST application monitored with Prometheus, Alertmanager, and Grafana. All easily to run with `docker-compose <src/docker-compose.yaml>`_

The live-demo consists of a Flask application and configured prometheus with grafana and alertmanager. To make it event easier, a request generator will let you stress the monitored endpoints with random errors and latency injections. Check the READMEs.

Related Work
============

- https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/
- http://www.brendangregg.com/usemethod.html
- https://github.com/prometheus/client_golang/blob/master/examples/random/main.go
- https://medium.com/@copyconstruct/logs-and-metrics-6d34d3026e38
- https://github.com/vegasbrianc/prometheus#post-configuration
- http://web.mit.edu/2.75/resources/random/How%20Complex%20Systems%20Fail.pdf
- https://www.slideshare.net/roidelapluie/prometheus-for-the-traditional-datacenter
- https://medium.com/@copyconstruct/logs-and-metrics-6d34d3026e38
- https://www.slideshare.net/brianbrazil/evolving-prometheus-for-the-cloud-native-world-fosdem-2018-brussels
