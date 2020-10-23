docker container run -it \
    -v /home/alex/proj/hepatoendo/app/data:/app/data \
    -p 127.0.0.1:8001:8000 \
    hepapp \
    gunicorn -b 0.0.0.0:8000 src.app:server
