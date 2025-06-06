#!/bin/bash

scenario=$1
SHORT=t:,c:
LONG=--tc_base:,conf:
OPTS=$(getopt --options $SHORT --longoptions $LONG -- "$@")
echo $1 $OPTS
