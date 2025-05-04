from fastapi import FastAPI
from prometheus_client import make_asgi_app, Counter, Histogram

app = FastAPI(title="Demo API con Prometheus")

# Métricas
REQUEST_COUNT = Counter(
    "api_request_count", "Total de peticiones HTTP recibidas",
    ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "Latencia de peticiones HTTP",
    ["method", "endpoint"]
)

# Instrumentación ASGI para /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    method = request.method
    endpoint = request.url.path
    with REQUEST_LATENCY.labels(method, endpoint).time():
        response = await call_next(request)
    REQUEST_COUNT.labels(method, endpoint).inc()
    return response

@app.get("/")
async def read_root():
    return {"message": "¡Hola desde FastAPI!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}