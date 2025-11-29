#!/usr/bin/env bash
pkill -f app_factory.py || true
pkill -f 'celery -A tasks.celery_app worker' || true
pkill -f redis-server || true
