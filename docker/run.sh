#!/bin/bash

/etc/init.d/redis-server start
/etc/init.d/postgresql start
a2enmod proxy
a2enmod proxy_http
/etc/init.d/apache2 start
cron
touch /var/log/cron.log
/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
