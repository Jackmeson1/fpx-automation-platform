#!/bin/bash

# SERVER
SERVER=172.18.29.116
USER=leo
PW=leo


RUN=/Project/PySystem/sysrunner/run.py
SCENARIO=/Project/FPX/TestCases/7.0.0/FortiProxy/Policy-Matching/policy-matching.csv
TC_BASE=/Project/FPX/TestCases/7.0.0
CONF=/Project/fpx_auto/environment/properties.json

FAIL_ACTION=
LOG_LEVEL=
DEBUG=
VERBOSE=1

function report(){
    sleep 5
    xdg-open "http://$SERVER/pysystem/logs/current/scenario.html"

}

if [ -n "$SERVER" ]; then
    if [[ -z $USER || -z $PW ]]; then
	echo "USER of server should be specified."
	exit -1
    else
	#report &
	#sshpass -p$PW ssh $USER@$SERVER -X
	sleep 1
    fi
else
    SERVER=localhost
    report &
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

#print "$CMD"
sshpass -p$PW ssh $USER@$SERVER -X /bin/bash <<EOF
    ls
EOF

#$CMD

