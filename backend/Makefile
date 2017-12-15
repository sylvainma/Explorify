init:
	pip install -r requirements.txt && docker pull mongo && export FLASK_APP=main.py

run:
	flask run

mongo:
	docker run --name explorify-mongo -d -p 27017:27017 mongo

kill: 
	sudo docker kill explorify-mongo

rm:
	sudo docker rm -f $$(docker ps -a -q)