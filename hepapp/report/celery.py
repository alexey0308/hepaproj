from celery import Celery
import os

BROKER_URL = os.getenv("BROKER_URL") or "pyamqp://guest@localhost//"

RESULT_BACKEND = "file:///app/images/"

app = Celery(__name__, broker=BROKER_URL, backend=RESULT_BACKEND)
app.conf.update(result_expires = 10)

if __name__ == "__main__":
    app.start()
