bme680-to-graphite
==================

Read all sensors on bme680 and send to graphite.

first install the sensor hardware
https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout

then set up Graphite, Grafana
https://markinbristol.wordpress.com/2015/09/20/setting-up-graphite-api-grafana-on-a-raspberry-pi/

but use nginx for forwarding to graphite instead of apache
`cp graphite.nginx.conf /etc/nginx/sites-enabled/`

install script like `cp read-sensors.py /usr/local/bin/`
install systemd unit file like `cp sensors.service /lib/systemd/system/`
`systemctl daemon-reload`
`systemctl start sensors.service` 
