#!/bin/bash

#Local
WSL=1

# SERVER
SERVER=172.18.29.116
#SERVER=172.18.29.200
USER=test
PW=test


RUN=/Project/PySystem/sysrunner/run.py
SCENARIO=/Project/FPX/TestCases/mantis/7.0.0/794753/test.csv
#TC_BASE=/Project/FPX/TestCases/mantis/7.0.0/794753
CONF=/Project/FPX/TestCases/mantis/7.0.0/794753/properties.json

SKIP_FIXTURE=0
FAIL_ACTION="continue"
#FAIL_ACTION="stop"
LOG_LEVEL=
DEBUG=0
VERBOSE=1

function report(){
    url="http://$1/pysystem/logs/current/scenario.html"
    #browser=$(xdg-settings get default-web-browser)
    #killall browser
    if (( $WSL != 0 )); then export BROWSER=wslview; fi
    sleep 5
    #xdg-open $url
    python3 -mwebbrowser -n $url

}

if [ -n "$SERVER" ]; then
    if [[ -z $USER ]]; then
	echo "USER of server should be specified."
	exit -1
    #else
	#report &
	#sshpass -p$PW ssh $USER@$SERVER -X
    fi
else
    SERVER=localhost
    #report &
fi

if [[ -z $RUN || -z $SCENARIO ]]; then
    echo "RUN file and SCENARIO file on the server must be specified."
    exit -1
fi

CMD="$RUN $SCENARIO"
if [[ -n $TC_BASE ]]; then 
    CMD="$CMD -t$TC_BASE"
#else
#    echo "TC_BASE folder on the server must be specified."
#    exit -1
fi
    
if [[ -n $CONF ]]; then CMD="$CMD -c$CONF"; fi
if [[ -n $FAIL_ACTION ]]; then CMD="$CMD -A$FAIL_ACTION"; fi
if [[ -n $LOG_LEVEL ]]; then CMD="$CMD -L$LOG_LEVEL"; fi
if (( $DEBUG != 0 )); then CMD="$CMD -D"; fi
if (( $VERBOSE != 0 )); then CMD="$CMD -v"; fi
if (( $SKIP_FIXTURE != 0 )); then CMD="$CMD -sk"; fi
echo "run command on server: $CMD"

if [[ -n $SERVER ]]; then
    report $SERVER &
    sshpass -p$PW ssh $USER@$SERVER -X /bin/bash <<EOF
        $CMD
EOF
else
    report "localhost" &
    $CMD
fi
