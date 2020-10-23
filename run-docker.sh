docker container run -it \
    -v "$PWD":/app \
    -p 127.0.0.1:8001:8000 \
    --name kiapp \
    --restart always \
    hepapp \
    gunicorn --reload -b 0.0.0.0:8000 src.app:server --pythonpath=src
