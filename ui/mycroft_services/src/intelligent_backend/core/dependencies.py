from functools import lru_cache
from burr.core import Application
from burr.core.project import Project

# Import the application factory functions from your workflow modules
from intelligent_backend.workflows.extraction.insight_extraction import create_insight_extraction_application
from intelligent_backend.workflows.extraction.policy_extraction import create_policy_extraction_application

# The name of the project. This should match the `project_id` in the telemetry server.
# It's also used to connect to the Burr UI.
PROJECT_NAME = "intelligent_backend"
# The address of the telemetry server. We'll use a service name for Docker Compose.
BURR_UI_URL = "http://burr-ui:7241"

@lru_cache(maxsize=1)
def get_insight_extraction_app() -> Application:
    """
    Dependency factory for the Burr insight extraction application.
    It now includes a tracker to send data to the telemetry server.
    """
    print("Initializing Burr Insight Extraction application with telemetry...")
    # The `with_tracker` method configures the application to send telemetry.
    # We point it to our project and the running telemetry server.
    app = create_insight_extraction_application().with_tracker(
        project=PROJECT_NAME, server_url=BURR_UI_URL, params={}
    )
    return app

@lru_cache(maxsize=1)
def get_policy_extraction_app() -> Application:
    """
    Dependency factory for the Burr policy extraction application.
    It now includes a tracker to send data to the telemetry server.
    """
    print("Initializing Burr Policy Extraction application with telemetry...")
    app = create_policy_extraction_application().with_tracker(
        project=PROJECT_NAME, server_url=BURR_UI_URL, params={}
    )
    return app
