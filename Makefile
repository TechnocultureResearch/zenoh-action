COMPOSE_DIR:=test

MINIMAL:=${COMPOSE_DIR}/minimal.yml
STANDALONE:=${COMPOSE_DIR}/standalone.yml

dash:
	docker compose -f ${MINIMAL} up

buildmin:
	docker compose -f ${MINIMAL} build

standalone:
	docker compose -f ${STANDALONE} up

build:
	docker compose -f ${STANDALONE} build
