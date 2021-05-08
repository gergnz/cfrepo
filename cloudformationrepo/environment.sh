#!/usr/bin/env bash
declare -p | grep -E "AWS|S3|DYNAMODB|LOG" > /container.env
