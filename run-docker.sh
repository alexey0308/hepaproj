docker container run -it --rm \
    -v "$PWD"/data-test:/app/data \
    -p 127.0.0.1:8001:8000 \
    --name kiapp \
    hepapp \
    gunicorn --reload -b 0.0.0.0:8000 hepapp.app:server --pythonpath=hepapp

# --restart always \
