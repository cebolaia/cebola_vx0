#!/bin/bash
airflow db init
flask fab create-admin --username admin --password admin --email admin@example.com -f Admin -l User
