apt-get -y install expect
expect /openscan/openvas_install.expect
/bin/expect /openscan/openvas_install.expect
/sbin/expect /openscan/openvas_install.expect
/usr/bin/expect /openscan/openvas_install.expect
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