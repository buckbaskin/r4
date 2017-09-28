## Broker settings.
broker_url = 'amqp://guest:guest@localhost:5672//'

# List of modules to import when the Celery worker starts.
imports = ('r4.streaming.billing',)

## Using the database to store task state and results.
# result_backend = 'db+sqlite:///results.db'

task_annotations = {'tasks.add': {'rate_limit': '10/s'}}

task_default_queue = 'celery'

task_routes = {
    # 'celery.ping': 'default',
    # 'mytasks.add': 'cpu-bound',
    'r4.streaming.billing.batch*': 'batch',
}
