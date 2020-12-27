SHELL = /bin/bash
.SILENT:

install:
	echo Creating virtualenv
	python3.6 -m pip install --upgrade pip
	python3.6 -m pip install virtualenv
	python3.6 -m virtualenv .env

	echo Installing requirements
	source .env/bin/activate && pip install -r requirements.txt

	echo Done

run:
	if [ "$(filter-out $@,$(MAKECMDGOALS))" == "dev" ] ; then \
		echo "Running 'dev' app on 127.0.0.1:8081"; \
		source .env/bin/activate && \
		rm nohup.out && nohup gunicorn -b 0.0.0.0:8081 run:app --reload --pid gunicorn.pid & \
	elif [ "$(filter-out $@,$(MAKECMDGOALS))" == "prod" ] ; then \
		echo "Running 'prod' app on 127.0.0.1:8082"; \
		source .env/bin/activate && \
		rm nohup.out && nohup gunicorn -b 0.0.0.0:8082 run:app --threads 2 --pid gunicorn.pid & \
	fi;

stop:
	echo Stopping app
	kill `cat gunicorn.pid`

restart:
	@make stop

	echo Please wait 1 min
	sleep 60

	@make run dev

shell:
	source .env/bin/activate && python3.6

logs:
	tail -f -n 30 nohup.out

%:
	@:
