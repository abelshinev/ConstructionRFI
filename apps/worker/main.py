import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

app = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)

# Configure Celery
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@app.task(name="test_task")
def test_task(x, y):
    print(f"Executing task test_task with x={x}, y={y}", flush=True)
    return x + y

if __name__ == "__main__":
    app.start()
