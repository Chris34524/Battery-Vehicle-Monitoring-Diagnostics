from fastapi import FastAPI

app = FastAPI(
    title="Battery & Vehicle Monitoring API",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "battery-vehicle-monitoring-api",
        "version": "0.1.0",
    }
