import os
import time

from celery import Celery

from .gennifer_api import generateInputs, run, parseOutput

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.conf.task_routes = {"create_bkb_grn_task": {"queue": 'bkb_grn'}}

@celery.task(name="create_bkb_grn_task")
def create_bkb_grn_task(zenodo_id, palim):
    data, feature_states, srcs = generateInputs(zenodo_id)
    res = run(data, feature_states, srcs, palim)
    output = parseOutput(res)
    return output
