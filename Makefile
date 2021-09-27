init: ## Initializes docker volume names and network for db
	docker volume create mysql
	docker volume create mysql_config
	docker network create mysqlnet

build-and-run: # creates flask server and mysql db
	docker-compose up --build

run:
	docker-compose up
	
clean: # removes all images/containers
	docker container rm -f python-docker-tutorial_mysqldb_1
	docker container rm -f python-docker-tutorial_web_1
	docker image rm -f image python-docker-tutorial_web:latest
	docker image rm -f image mysql:latest

destroy: clean 
	docker volume rm -f mysql
	docker volume rm -f mysql_config
	docker volume rm -f python-docker-tutorial_mysql
	docker volume rm -f python-docker-tutorial_mysql_config
	rm -rf images
	mkdir images