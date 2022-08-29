# storagebox-expire
Manage backups on remote storagebox (e.g. hetzner). Delete expired backups.

## List backups
~~~shell
$ storagebox-expire.py uNNNNNN.your-storagebox.de -p 23 -u uNNNNN --list
2022-08-29 16:50 started
Daily:
d5s-2022-08-29.tar.gz: d5s 2022-08-29 00:00:00
liste-2022-08-29.tar.gz: liste 2022-08-29 00:00:00
signal-2022-08-29.tar.gz: signal 2022-08-29 00:00:00

Monthly:
d5s-2022-07-22.tar.gz: d5s 2022-07-22 00:00:00
liste-2022-08-29.tar.gz: liste 2022-08-29 00:00:00
signal-2022-08-29.tar.gz: signal 2022-08-29 00:00:00

~~~

## Create monthly backups
~~~shell
$ storagebox-expire.py uNNNNNN.your-storagebox.de -p 23 -u uNNNNN --mkmonthly
2022-08-29 16:45 started
Daily:
d5s-2022-08-29.tar.gz: d5s 2022-08-29 00:00:00
liste-2022-08-29.tar.gz: liste 2022-08-29 00:00:00
signal-2022-08-29.tar.gz: signal 2022-08-29 00:00:00

Monthly:
d5s-2022-07-22.tar.gz: d5s 2022-07-22 00:00:00
liste-2022-08-29.tar.gz: liste 2022-08-29 00:00:00

UPDATE /home/daily/signal-2022-08-29.tar.gz /home/monthly
Copied 1 backups
~~~

## Delete expired backups
~~~shell
$ storagebox-expire.py uNNNNNN.your-storagebox.de -p 23 -u uNNNNN --expire 35
2022-08-29 17:17 started
=== d5s
DELETE /home/daily/d5s-2022-07-21.tar.gz
DELETE /home/daily/d5s-2022-07-22.tar.gz
DELETE /home/daily/d5s-2022-07-23.tar.gz
DELETE /home/daily/d5s-2022-07-24.tar.gz
=== liste
DELETE /home/daily/liste-2022-07-20.tar.gz
DELETE /home/daily/liste-2022-07-21.tar.gz
DELETE /home/daily/liste-2022-07-22.tar.gz
DELETE /home/daily/liste-2022-07-23.tar.gz
DELETE /home/daily/liste-2022-07-24.tar.gz

...
~~~