#AD SIM

### Concept: Fake users send logs to a fake ad server




In `simulate_behavior`, a population of users generate preferences among a set of brands.

They browse along through the brands' products and, if shown an ad, will either like the brand more (if already predisposed) or like them less (if truly an 'unqualified audience'). Each brand has its own normal distribution describing its product mix.

Every once in a while, a user will consider purchase. If their brand preferences are low variance, they'll leave without buying. If their brand preferences are high variance, they'll buy their favorite brand.

The tracking server, `receiver`, records user information in redis and decides whether to display an ad on each page. Showing an ad before being confident the user likes a brand risks turning them off the brand. Not showing ads means the users' preferences will likely remain low variance and they'll leave without purchasing.

### Usage:

This is definitely still a toy situation on a laptop, but there're several components:

* Redis, for tracking users (I'm just running redis-server on localhost)
* Kafka, for passing impressions (I'm running spotify/kafka in docker, using docker-machine)
* The Flask server: run `python wsgi.py`, for handling requests
* The redis-updating worker: run python manage.py track to consume impressions


### Kafka via Docker:

Spotify offers a combined zookeeper and kafka Docker image.

Not too hard to get this running with Docker-machine.

Get a VM: `docker-machine start default`

Get its variables: `eval "$(docker-machine env default)"`

Run the image:
`docker run -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=`docker-machine ip default` --env ADVERTISED_PORT=9092 spotify/kafka`

Then you can use the Apache kafka scripts to do some setup from your own machine, provided you've installed these (via `brew install kafka`):
```
export KAFKA=`docker-machine ip default`:9092

export ZOOKEEPER=`docker-machine ip default`:2181

kafka-topics.sh --create --zookeeper $ZOOKEEPER --replication-factor 1 --partitions 1 --topic page_views
```
