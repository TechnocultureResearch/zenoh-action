COMPOSE_DIR:=test

MINIMAL:=./${COMPOSE_DIR}/minimal.yml
STANDALONE:=./${COMPOSE_DIR}/standalone.yml

ACTION_FILE:=action.json
DASHBOARD_DATA:=dashboard/src/data

all: build_min min

min:
	docker compose -f ${MINIMAL} up

build_min:
	docker compose -f ${MINIMAL} build

main:
	docker compose -f ${STANDALONE} up

build_main:
	docker compose -f ${STANDALONE} build

symlink:
	ln -sf ${PWD}/${ACTION_FILE} ${PWD}/${DASHBOARD_DATA}/${ACTION_FILE}
