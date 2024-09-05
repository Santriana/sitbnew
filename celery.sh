#!/bin/bash

set -o errexit
set -o nounset

celery -A usaid worker -l info -P solo