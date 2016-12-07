#!/bin/bash
. /etc/init.d/functions

start() {
	if [ ! -f /root/installed_openvas ]; then
	echo "#step1" > /root/installed_openvas_steps
		apt-get -y install openvas
	echo "#step2" > /root/installed_openvas_steps
		openvas-nvt-sync
	echo "#step3" > /root/installed_openvas_steps
		openvas-scapdata-sync
	echo "#step4" > /root/installed_openvas_steps
		openvas-certdata-sync
	echo "#step5" > /root/installed_openvas_steps
		service openvas-scanner restart
	echo "#step6" > /root/installed_openvas_steps
		service openvas-manager restart
	echo "#step7" > /root/installed_openvas_steps
		service openvasmd --rebuild --progress
	echo "#step8" > /root/installed_openvas_steps
		openvasmd-stop
	echo "#step9" > /root/installed_openvas_steps
		openvasmd --create-user=vulscan --role=Admin
	echo "#step10" > /root/installed_openvas_steps
		openvasmd --user=vulscan --new-password=vulscan
	echo "#step11" > /root/installed_openvas_steps
		openvasmd-start
	echo "#step12" > /root/installed_openvas_steps
		echo "-" > /root/installed_openvas
	fi
}

stop() {
}

case "$1" in 
    start)
       start
       ;;
    stop)
       stop
       ;;
    restart)
       stop
       start
       ;;
    status)
       ;;
    *)
       echo "Usage: $0 {start|stop|status|restart}"
esac

exit 0 
