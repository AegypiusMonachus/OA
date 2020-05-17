#!/bin/bash


INI_FILE="uwsgi/uwsgi.ini"
PID_FILE="uwsgi/uwsgi.pid"


if [ $1 == "start" ]; then
	source venv/bin/activate
	uwsgi $INI_FILE > /dev/null 2>&1 &

	sleep 1; echo -n .
	sleep 1; echo -n .
	sleep 1; echo -n .
	sleep 1; echo

	echo
	ps -ef | grep "KRAKEN_BACKOFFICE"
	echo
	ps -ef | grep "KRAKEN"
fi


if [ $1 == "stop" ]; then
	source venv/bin/activate
	uwsgi --stop $PID_FILE

	sleep 1; echo -n .
	sleep 1; echo -n .
	sleep 1; echo -n .
	sleep 1; echo

	echo
	ps -ef | grep "KRAKEN_BACKOFFICE"
	echo
	ps -ef | grep "KRAKEN"
fi
