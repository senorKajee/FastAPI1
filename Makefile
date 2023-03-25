.PHONY: install start start_worker destroy 

install:
	pip install -r requirements.txt

start:
	python ./app/main.py

start_worker: 
	celery -A consumer.celery worker --loglevel=INFO  --concurrency=2 -E

compose:
	./startReplicaSetEnvironment.sh

destroy:
	docker compose down

	
	