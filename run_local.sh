#!/bin/bash

source ./keys/keys.sh
supervisord -c ./files/supervisor_local.conf
