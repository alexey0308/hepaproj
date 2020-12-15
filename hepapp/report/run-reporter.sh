#!/bin/bash

gunicorn -b 0.0.0.0:5080 hepapp.report.app:app --reload -t 300 --daemon
celery --app=hepapp.report.tasks:app worker -l INFO
