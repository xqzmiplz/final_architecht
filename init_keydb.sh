#!/bin/bash
keydb-server --dir /data & # Запускаем KeyDB в фоновом режиме

until keydb-cli ping; do
  echo "Waiting for KeyDB to be ready..."
  sleep 1
done


keydb-cli <<EOF
SET student:BSBO-01-20:15 "KEKW"
HSET student:BSBO-01-20:15:info name "Keww" age 22 email "your_email@misis.edu"
LPUSH student:BSBO-01-20:15:timetable "Programming" "Data bases" "Architecht"
SADD student:BSBO-01-20:15:skills Docker Python Flask Redis RabbitMQ
ZADD student:BSBO-01-20:15:tasks_w_priority 100 "Pass laba 2" 150 "Pass laba 3"
LPUSH student:BSBO-01-20:15:timetable "English"
LREM student:BSBO-01-20:15:timetable 1 "Databases"
SREM student:BSBO-01-20:15:skills "Flask"
HGET student:BSBO-01-20:15:info name
ZREM student:BSBO-01-20:15:tasks_w_priority "Pass laba 2"
EXPIRE student:BSBO-01-20:15 3600
TTL student:BSBO-01-20:15
PERSIST student:BSBO-01-20:15
EOF

tail -f /dev/null