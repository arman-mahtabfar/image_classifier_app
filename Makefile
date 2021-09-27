init: ## Initializes docker volume names and network for db
	docker volume create mysql
	docker volume create mysql_config
	docker network create mysqlnet

build-and-run: # creates flask server and mysql db
	docker-compose up --build
	docker rmi $(docker images -f “dangling=true” -q)

run:
	docker-compose up
	
clean: # removes all images/containers
	docker container rm -f tensorflow_vgg16_classifier_mysqldb_1
	docker container rm -f tensorflow_vgg16_classifier_web_1
	docker image rm -f image tensorflow_vgg16_classifier_web:latest
	docker image rm -f image mysql:latest

destroy: clean 
	docker volume rm -f mysql
	docker volume rm -f mysql_config
	docker volume rm -f tensorflow_vgg16_classifier_mysql
	docker volume rm -f tensorflow_vgg16_classifier_mysql_config
	rm -rf images
	mkdir images