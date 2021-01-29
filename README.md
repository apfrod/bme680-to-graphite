bme680-to-graphite
==================

Read all sensors on bme680 and send to graphite on raspberry pi.

first install the sensor hardware
https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout

then set up carbon, graphite-api & grafana
https://markinbristol.wordpress.com/2015/09/20/setting-up-graphite-api-grafana-on-a-raspberry-pi/
`sudo apt install graphite-carbon`
edit /etc/default/graphite-carbon and change CARBON_CACHE_ENABLED to true
`sudo apt install python python-pip build-essential python-dev libcairo2-dev libffi-dev`
`sudo pip install graphite-api`
`sudo cp graphite-api.yaml /etc/graphite-api.yaml`

nb ok to install latest grafana 

install gunicorn to serve the graphite http api
'sudo pip install gunicorn'

and add the systemd service for gunicorn
`sudo cp graphite-api.socket /etc/systemd/system/graphite-api.socket`
`sudo p graphite-api.service /etc/systemd/system/graphite-api.service`
`sudo systemctl enable graphite-api.socket`
`sudo systemctl start graphite-api.service`

but use nginx for forwarding to graphite instead of apache
`sudo cp graphite.nginx.conf /etc/nginx/sites-enabled/`

install script like `cp read-sensors.py /usr/local/bin/`
install systemd unit file like `cp sensors.service /lib/systemd/system/`
`sudo systemctl daemon-reload`
`sudo systemctl start sensors.service` 

edit /etc/grafana/grafana.ini http_port to set port
visit pi_ip:port to get grafana frontend

add graphite-api source in grafana: http://localhost:8888
import dashboard.json cwin grafana
