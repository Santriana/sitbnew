#!/bin/bash

set -o errexit
set -o nounset

celery -A usaid beat -l info