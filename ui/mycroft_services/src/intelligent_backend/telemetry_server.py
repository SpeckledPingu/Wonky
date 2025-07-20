import uvicorn
from burr.integrations.server import create_server

# This is the main entry point for the Burr Telemetry & UI Server.
# It doesn't need to know about any specific application logic.
# It just needs a project ID to group the telemetry data.
# The project ID should match what's configured in your main application's trackers.
app = create_server(project_id="intelligent_backend")

if __name__ == "__main__":
    # The server will run on port 7241 by default.
    # This can be configured if needed.
    # The host '0.0.0.0' makes it accessible from outside its container.
    print("Starting Burr Telemetry UI Server on http://0.0.0.0:7241")
    uvicorn.run(app, host="0.0.0.0", port=7241)
