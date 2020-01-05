"""
 Copyright [2019] [Mauro Riva <info@lemariva.com> <lemariva.com>]

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
"""

import gc
import machine
import time

from microWebSrv import MicroWebSrv

# Initialize light PWM, flash for 1/4 sec on boot
train = machine.Pin(12, machine.Pin.OUT)
train_pwm = machine.PWM(train)
train_pwm.freq(10000)
train_pwm.duty(0)

def _httpHandlerIndex(httpClient, httpResponse):
    content = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>wESP32 Train Control</title>
    <meta name="robots" content="index,follow">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body onload="updateslider()">
  
    <div class="container content">
      <div class="page-header">
        <img src="https://lemariva.com/themes/lemariva/assets/images/uikit/logo-text.svg" alt="LeMaRiva|tech">
      </div>
      <div class="panel panel-default">
        <div class="panel-body">
        <section class="section-preview">
          <label for="lightlevel">Train speed:</label>
          <input type="range" min="0" max="800" value="0" step="5" class="slider custom-range" id="lightlevel" style="width: 100%;">
        </section>
        </div>
        </div>

        <footer class="footer">
          <div class="container">
            <span class="text-muted"><a href="https://lemariva.com">LeMaRiva|tech</a></span>
          </div>
        </footer>
    </div>

    <script>
        var slider = document.getElementById("lightlevel");
        var update_track = 0;
        var update_input = 0;

        function updateslider(level) {
            update_track++;
            var this_update = update_track;
            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200 && (!update_input || this_update == update_input)) {
                    slider.value = parseInt(this.responseText);
                    update_input = 0;
                }
            };
            if (typeof(level) !== 'undefined') {
                update_input = this_update;
                xhttp.open("GET", "train/level/" + level, true);
            } else {
                xhttp.open("GET", "train", true);
            }
            xhttp.send();
        }

        slider.onchange = function() {
            console.log(this.value);
            updateslider(this.value);
        }
    </script>    
            
    </body>
    </html>
    """
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)


def _httpHandlerSetTrainSpeed(httpClient, httpResponse, routeArgs):
    pwm_level = int(routeArgs['level'])
    train_pwm.duty(pwm_level)

    content = """\
        {}
        """.format(train_pwm.duty())
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)

def _httpHandlerGetTrainSpeed(httpClient, httpResponse):
    content = """\
        {}
        """.format(train_pwm.duty())
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)

def _httpHandlerMemory(httpClient, httpResponse, routeArgs):
    query = str(routeArgs['query'])

    if 'gc' in query or 'collect' in query:
        gc.collect()

    content = """\
        {}
        """.format(gc.mem_free())
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)

routeHandlers = [
    ("/", "GET", _httpHandlerIndex),
    ("/train/level/<level>", "GET", _httpHandlerSetTrainSpeed),
    ("/train", "GET", _httpHandlerGetTrainSpeed),
    ("/memory/<query>", "GET", _httpHandlerMemory)
]

def run():
    mws = MicroWebSrv(routeHandlers=routeHandlers, webPath="www/")
    mws.Start(threaded=True)
    gc.collect()