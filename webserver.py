import machine
import picoweb
import time
import gc

# Initialize light PWM, flash for 1/4 sec on boot
train = machine.Pin(12, machine.Pin.OUT)
train_pwm = machine.PWM(train)
train_pwm.freq(10000)
train_pwm.duty(0)

# Picoweb instance
app = picoweb.WebApp(__name__)

# Parse a query string into a dictionary with key/value pairs
def parse_query(qs):
    if len(qs) > 0:
        return dict([pair.split('=', 1) if '=' in pair else (pair, None)
                    for pair in qs.split('&')])
    else:
        return {}

# Home page
@app.route("/")
def index(req, resp):
    yield from picoweb.start_response(resp, content_type = "text/html")
    htmlFile = open('www/index.html', 'r')
    for line in htmlFile:
        yield from resp.awrite(line)

# Image load
@app.route("/logo-text.svg")
def image_load(req, resp):
    yield from picoweb.start_response(resp, content_type = "image/svg+xml")
    htmlImage = open('www/logo-text.svg', 'r')
    for line in htmlImage:
        yield from resp.awrite(line)

# Update train speed
@app.route("/train")
def train(req, resp):
    query = parse_query(req.qs)
    if 'level' in query:
        train_pwm.duty(int(query['level']))
    yield from picoweb.start_response(resp, content_type = "text/plain")
    yield from resp.awrite(str(train_pwm.duty()))
    yield from resp.aclose()

# Memory info
@app.route("/memory")
def light(req, resp):
    query = parse_query(req.qs)
    if 'gc' in query or 'collect' in query:
        gc.collect()
    yield from picoweb.start_response(resp, content_type = "text/plain")
    yield from resp.awrite(str(gc.mem_free()))
    yield from resp.aclose()

# Run Picoweb server
def run():
    app.run(host='0.0.0.0', port=80, debug=True)
