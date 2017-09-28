from r4.streaming import celery_app as app
# AWS tracks storage (GB/month), requests (# of GET, etc) and bandwidth
# stream processing to determine

# Pipeline:
# every S3 request ever is paired with a log item added to the first queue
# Every log item is parsed into an "S3" event
# S3 events are used to track costs. For example:
# a PUT call to upload an object: indicates size, starts a tracker to keep track of GB per month per user tracker, increments a counter for the number of PUT requests, and increments bandwidth used 

def S3_storage_pricing(gb_used, months_used, region):
    gb_months = float(gb_used) * float(months_used)
    tb_months = gb_months / 1024
    if tb_months <= 50:
        return gb_months * 0.023
    elif tb_months <= 500:
        return 50 * 1024 * 0.023 + (gb_months - 50 * 1024) * 0.022
    else:
        return 50 * 1024 * 0.023 + 450 * 1024 * 0.022 + (gb_months - 500 * 1024) * 0.021

def S3_bandwidth_out_pricing(gb_used, region):
    if gb_used <= 1:
        return gb_used * 0.0
    elif gb_used <= 10 * 1024:
        return (gb_used - 1) * 0.090 + 1 * 0.000
    elif gb_used <= 50 * 1024:
        return (gb_used - 10 * 1024) * 0.085 + (10 * 1024 - 1) * 0.090
    elif gb_used <= 150 * 1024:
        return (gb_used - 50 * 1024) * 0.070 + 40 * 1024 * 0.085 + (10 * 1024 - 1) * 0.090
    else: # technically up to 500TB, after that, call them
        return (gb_used - 150 * 1024) * 0.050 + 100 * 1024 * 0.070 + 40 * 1024 * 0.085 + (10 * 1024 - 1) * 0.090

def S3_bandwidth_in_pricing(gb_used, region):
    return 0.000

def S3_request_pricing(request, quantity):
    pricing_info = {
        'put': (0.005, 1000),
        'copy': (0.005, 1000),
        'post': (0.005, 1000),
        'list': (0.005, 1000),
        'get': (0.004, 10000),
        'delete': (0.00, 1000),
        'default': (0.004, 10000),
    }[request.lower()]
    units = ceil(quantity / pricing_info[1])
    return pricing_info[0] * units


class Event(object):
    def __init__(self, timestamp, username, type_, size):
        self.timestamp = timestamp # in UTC
        self.username = username # string
        self.type_ = type_ # string, GET, POST, etc.
        self.size = size # MB
@app.task
def handle_event(event_json):
    pass

@app.task
def parse_text_event(text_event):
    # convert a text event into a standard format
    # then put it back into the queue for processing
    # TODO: get event time, get event user, get event request type, get event size
    # specify that the text event come in as JSON with requisite info
    # use this info to parse to the correct events
    e = Event(datetime.now(), 'example_user', 'GET', 0.050)
    handle_event.apply_async(args=[e.to_json()])

    ### These get called on a schedule
    #  batch_update.delay('bandwidth')
    #  batch_update.delay('storage')
    #  batch_update.delay('requests')

local_data = {
    'bandwidth': None,
    'storage': None,
    'requests': None,
}

def update_local_storage(event):
    pass

def update_local_bandwidth(event):
    pass

def update_local_requests(event):
    # write a requests increment for a username-service
    pass

update_local = {
    'bandwidth': update_local_bandwidth,
    'storage': update_local_storage,
    'requests': update_local_requests,
}

def write_local_to_s3(event):
    pass


@app.task
def batch_update(param):
    # process event and accumulate its additional bandwidth cost
    # write a bandwidth incrememnt for a username-service
    global local_data
    if local_data[param] is None:
        # TODO(buckbaskin): load from s3
        local_data[param] = {}

    global app
    with app.amqp.Connection(app.conf['BROKER_URL']) as conn:
        queue_name = 'batch_%s' % (param,)
        q = conn.SimpleQueue(queue_name)
        number = conn.manager.get_queue_depth('/', queue_name)
        messages = []
        for _ in range(number):
            try:
                messages.append(q.get(timeout=.1))
            except Empty:
                break

        for message in messages:
            event = json.loads(message.decode()['args'][0])
            update_local[param](event)

        write_local_to_s3(local_data)
        
@app.task
def calculate_bill(username):
    # aggregate all of the billed actions for the given user
    # accumulate storage, bandwidth and request actions across services for a user at the time of the request
    pass
