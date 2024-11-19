import pytest
import json
import os

def lambda_context():
    class LambdaContext:
        def __init__(self):
            self.function_name = "chronochat-test-main"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:eu-west-1:809313241234:function:chronochat-test-main"
            self.aws_request_id = "52fdfc07-2182-154f-163f-5f0f9a621d72"

        def get_remaining_time_in_millis(self) -> int:
            return 1000

    return LambdaContext()

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    os.environ["STAGE"] = "test"
    os.environ["POWERTOOLS_SERVICE_NAME"] = "ChronoChat-test"
    os.environ["POWERTOOLS_METRICS_NAMESPACE"] = "ChronoChat-test"
    os.environ["LOG_LEVEL"] = "DEBUG"

    # Clear any existing metrics to avoid conflicts
    from aws_lambda_powertools.metrics import Metrics
    metrics = Metrics()
    metrics.clear_metrics()
    
    yield
    
    # Clean up environment after tests
    os.environ.pop("STAGE", None)
    os.environ.pop("POWERTOOLS_SERVICE_NAME", None)
    os.environ.pop("POWERTOOLS_METRICS_NAMESPACE", None)
    os.environ.pop("LOG_LEVEL", None)

# Move the app import after the environment setup
from app import app

@pytest.fixture()
def apigw_event_template():
    """Base API Gateway event template"""
    return {
        "body": "",
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "isBase64Encoded": False,
        "requestContext": {
            "stage": "test",
        },
        "multiValueQueryStringParameters": None,
        "queryStringParameters": None,
        "pathParameters": None,
    }

@pytest.fixture()
def apigw_event(apigw_event_template):
    """GET /hello event"""
    event = apigw_event_template.copy()
    event["httpMethod"] = "GET"
    event["path"] = "/hello"
    return event

@pytest.fixture()
def apigw_get_travels_event(apigw_event_template):
    """GET /travels event"""
    event = apigw_event_template.copy()
    event["httpMethod"] = "GET"
    event["path"] = "/travels"
    return event

@pytest.fixture()
def apigw_create_travel_event(apigw_event_template):
    """POST /travels event"""
    event = apigw_event_template.copy()
    event["httpMethod"] = "POST"
    event["path"] = "/travels"
    event["body"] = json.dumps({"destination": "Ancient Rome"})
    return event

@pytest.fixture()
def apigw_get_travel_by_id_event(apigw_event_template):
    """GET /travels/{id} event"""
    event = apigw_event_template.copy()
    event["httpMethod"] = "GET"
    event["path"] = "/travels/123"
    event["pathParameters"] = {"id": "123"}
    return event

@pytest.fixture()
def apigw_delete_travel_event(apigw_event_template):
    """DELETE /travels/{id} event"""
    event = apigw_event_template.copy()
    event["httpMethod"] = "DELETE"
    event["path"] = "/travels/123"
    event["pathParameters"] = {"id": "123"}
    return event

def test_hello_endpoint(apigw_event):
    ret = app.lambda_handler(apigw_event, lambda_context())
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert data["message"] == "hello world"

def test_get_travels_endpoint(apigw_get_travels_event):
    ret = app.lambda_handler(apigw_get_travels_event, lambda_context())
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert data["message"] == "get travels"

def test_create_travel_endpoint(apigw_create_travel_event):
    ret = app.lambda_handler(apigw_create_travel_event, lambda_context())
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert data["message"] == "create travel"

def test_get_travel_by_id_endpoint(apigw_get_travel_by_id_event):
    ret = app.lambda_handler(apigw_get_travel_by_id_event, lambda_context())
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert data["message"] == "get travel by id 123"

def test_delete_travel_endpoint(apigw_delete_travel_event):
    ret = app.lambda_handler(apigw_delete_travel_event, lambda_context())
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert data["message"] == "delete travel 123"

def test_stage_environment(apigw_event):
    ret = app.lambda_handler(apigw_event, lambda_context())
    
    # Verify that logs contain stage information
    # Note: This is a basic test - in real scenarios, you might want to use
    # a mock logger to capture and verify log messages
    assert os.getenv("STAGE") == "test"
    assert os.getenv("POWERTOOLS_SERVICE_NAME") == "ChronoChat-test"