from celery import Celery

celery_app = Celery('billing', broker='pyamqp://guest@localhost//')



