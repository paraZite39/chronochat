import os

from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit

stage = os.getenv("STAGE")
metrics_namespace = os.getenv("POWERTOOLS_METRICS_NAMESPACE")

app = APIGatewayRestResolver()
tracer = Tracer()
logger = Logger()
metrics = Metrics(namespace=metrics_namespace)

@app.get("/hello")
@tracer.capture_method
def hello():
    # adding custom metrics
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/metrics/
    metrics.add_metric(name="HelloWorldInvocations", unit=MetricUnit.Count, value=1)

    # structured log
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/logger/
    logger.info(f"Hello world API - HTTP 200 - {stage}")
    return {"message": "hello world"}


@app.get("/travels")
@tracer.capture_method
def get_travels():
    metrics.add_metric(name="GetTravelsInvocations", unit=MetricUnit.Count, value=1)
    logger.info(f"Get travels API - HTTP 200 - {stage}")
    return {"message": "get travels"}


@app.post("/travels")
@tracer.capture_method
def create_travel():
    metrics.add_metric(name="CreateTravelInvocations", unit=MetricUnit.Count, value=1)
    logger.info(f"Create travel API - HTTP 200 - {stage}")
    return {"message": "create travel"}


@app.get("/travels/{id}")
@tracer.capture_method
def get_travel_by_id(id: str):
    metrics.add_metric(name="GetTravelByIdInvocations", unit=MetricUnit.Count, value=1)
    logger.info(f"Get travel by id API - HTTP 200 - {stage}")
    return {"message": f"get travel by id {id}"}


@app.delete("/travels/{id}")
@tracer.capture_method
def delete_travel(id: str):
    metrics.add_metric(name="DeleteTravelInvocations", unit=MetricUnit.Count, value=1)
    logger.info(f"Delete travel API - HTTP 200 - {stage}")
    return {"message": f"delete travel {id}"}


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
# Adding tracer
# See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/tracer/
@tracer.capture_lambda_handler
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
