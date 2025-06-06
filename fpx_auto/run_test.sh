#!/bin/bash

#Local
WSL=1

# SERVER of the pysystem tc running from
SERVER=172.18.29.116
# change this to your own user/pw when sharing the server with others to avoid conflict
USER=leo
PW=leo


RUN=/Project/PySystem/sysrunner/run.py
#SCENARIO=/Project/FPX/TestCases/7.0.0/FortiProxy/Policy-Matching/policy-matching.csv
SCENARIO=/Project/fpx_auto/test.csv
TC_BASE=/Project/FPX/TestCases/7.2.0
CONF=/Project/fpx_auto/lab_env/leo_lab.json

SKIP_FIXTURE=0
FAIL_ACTION="continue"
#FAIL_ACTION="stop"
LOG_LEVEL=
DEBUG=0
VERBOSE=1

REPORT_PATH="/pysystem/$USER" # Change this to your own url to avoid conflict

function report(){
    # url="http://$1/pysystem/logs/current/scenario.html"
    url="http://$1/$REPORT_PATH/logs/current/scenario.html"
    #browser=$(xdg-settings get default-web-browser)
    #killall browser
    if (( $WSL != 0 )); then export BROWSER=wslview; fi
    sleep 10
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
else
    echo "TC_BASE folder on the server must be specified."
    exit -1
fi
    
if [[ -n $CONF ]]; then CMD="$CMD -c$CONF"; fi
if [[ -n $FAIL_ACTION ]]; then CMD="$CMD -A$FAIL_ACTION"; fi
if [[ -n $LOG_LEVEL ]]; then CMD="$CMD -L$LOG_LEVEL"; fi
if (( $DEBUG != 0 )); then CMD="$CMD -D"; fi
if (( $VERBOSE != 0 )); then CMD="$CMD -v"; fi
if (( $SKIP_FIXTURE != 0 )); then CMD="$CMD -sk"; fi
CMD="$CMD -H $REPORT_PATH"

if [[ -n $SERVER ]]; then
    report $SERVER &
    sshpass -p$PW ssh $USER@$SERVER -X /bin/bash <<EOF
        $CMD
EOF
else
    report "localhost" &
    $CMD
fi
