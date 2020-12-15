from celery import Celery
import os

BROKER_URL = os.getenv("BROKER_URL") or "pyamqp://guest@localhost//"

app = Celery(__name__, broker=BROKER_URL)
app.conf.update(result_expires = 10)

if __name__ == "__main__":
    app.start()
