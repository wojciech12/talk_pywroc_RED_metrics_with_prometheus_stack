from flask import Flask, Response
from flask import request
from prometheus_client import (Summary, Histogram, generate_latest,
                               CollectorRegistry)
from prometheus_client import multiprocess
import ast
import time


class MetricCollector:

    def observe_myself(self, path, method, status_code, duration):
        self._me.labels(path=path, method=method,
                        status_code=status_code).observe(duration)

    def observe_db(self, status_code, sql_state, duration):
        self._db.labels(status_code=status_code,
                        sql_state=sql_state).observe(duration)

    def observe_external(self, status_code, duration):
        self._external.labels(status_code=status_code).observe(duration)

    def get_latest(self):
        return generate_latest()

    @staticmethod
    def newCollector(service_name):
        prefix = service_name.replace("-", "_")
        STATUS_CODE = 'status_code'
        PATH = 'path'
        HTTP_METHOD = 'method'

        about_me = Summary(prefix + "_duration_seconds",
                           service_name + " latency request distribution",
                           [PATH, HTTP_METHOD, STATUS_CODE])

        about_db = Histogram(prefix + "_database_duration_seconds",
                             "database latency request distribution",
                             [STATUS_CODE, 'sql_state'],
                             buckets=(.1, .25, .5, .75, .90, 1.0, 2.5))

        about_her = Summary(prefix + "_audit_duration_seconds",
                            "audit service latency request distribution",
                            [STATUS_CODE])

        mc = MetricCollector()
        mc._me = about_me
        mc._db = about_db
        mc._external = about_her
        return mc


def get_collector(name):
    return MetricCollector.newCollector(name)


def add_routes(app,  collector):
    @app.route('/hello')
    def hello_route():
        return 'hello'

    @app.route('/world')
    def world_route():
        return 'world'

    @app.route('/complex')
    def complex_operation():
        # getting data from db
        try:
            work_with_db(collector)
        except RuntimeError as re:
            r = Response("{0}".format(re), mimetype='text/plain')
            r.status_code = 503
            return r

        # calling an external service
        try:
            work_with_third_party(collector)
        except RuntimeError as re:
            r = Response("{0}".format(re), mimetype='text/plain')
            r.status_code = 503
            return r
        return 'Success!'


def work_with_db(collector):
    start_time = time.time()

    db_sleep = float(request.args.get("db_sleep", 0))
    is_db_error = ast.literal_eval(request.args.get("is_db_error", "False"))

    try:
        call_db(db_sleep, is_db_error)
        latency = time.time() - start_time
        collector.observe_db('0', '0', latency)
    except RuntimeError as re:
        """
        """
        latency = time.time() - start_time
        collector.observe_db('1001', 'HY000', latency)
        raise re


def call_db(db_sleep, is_error):
    mocked_call("Database XYZ", db_sleep, is_error)


def work_with_third_party(collector):
    start_time = time.time()
    srv_sleep = float(request.args.get("srv_sleep", 0))
    is_srv_error = ast.literal_eval(request.args.get("is_srv_error", "False"))

    try:
        call_external(srv_sleep, is_srv_error)
        latency = time.time() - start_time
        collector.observe_external('200', latency)
    except RuntimeError as re:
        """
        """
        latency = time.time() - start_time
        collector.observe_external('500', latency)
        raise re


def call_external(srv_sleep, is_error):
    mocked_call("Service Audit", srv_sleep, is_error)


def mocked_call(what, sleep, is_error):
    if sleep > 0:
        time.sleep(sleep)
    if is_error:
        raise RuntimeError(what + " failed to process request")


def instrument_requests(app, collector):
    import time

    def before():
        request.start_time = time.time()

    def after(response):
        if request.path != '/metrics':
            request_latency = time.time() - request.start_time
            collector.observe_myself(request.path,
                                     request.method,
                                     response.status_code,
                                     request_latency)
        return response

    app.before_request(before)
    app.after_request(after)


def add_metrics_route(app, collector):
    @app.route('/metrics', strict_slashes=False, methods=['GET'])
    def metrics_rotue():
        # txt = generate_latest()
        txt = get_latest_when_running_with_gunicorn()
        return Response(txt, mimetype='text/plain')


# you can skip *multiprocess_mode*
# if you do not need multiprocessing with gunicorn
# see https://github.com/prometheus/client_python#multiprocess-mode-gunicorn
def get_latest_when_running_with_gunicorn():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return generate_latest(registry)


def get_app():
    app = Flask(__name__)
    c = get_collector('order-mgmt')
    add_routes(app, c)
    add_metrics_route(app, c)
    instrument_requests(app, c)
    return app


if __name__ == "__main__":
    app = get_app()
    app.run(host='0.0.0.0',
            port=8080)
