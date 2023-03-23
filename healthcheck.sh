#!bin/bash
SERVER="server:12345"
MESSAGE="Hello World!"

RESPONSE=$(echo "$MESSAGE" | nc "$SERVER")
echo "$RESPONSE"

if [ "$RESPONSE" = "$MESSAGE" ]; then
  echo "OK"
else
  echo "ERROR"
fi