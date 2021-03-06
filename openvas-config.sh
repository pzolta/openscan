#!/bin/bash
apt-get -y install openvas
openvas-nvt-sync
openvas-scapdata-sync
openvas-certdata-sync
service openvas-scanner restart
service openvas-manager restart
service openvasmd --rebuild --progress
openvasmd-stop
openvasmd --create-user=vulscan --role=Admin
openvasmd --user=vulscan --new-password=vulscan
openvasmd-start
