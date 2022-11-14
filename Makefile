COMPOSE_DIR:=test

MINIMAL:=./${COMPOSE_DIR}/minimal.yml
MINIMAL_PY:=./${COMPOSE_DIR}/minimal-python.yml
STANDALONE:=./${COMPOSE_DIR}/standalone.yml

ACTION_FILE:=action.json
DASHBOARD_DATA:=dashboard/src/data

min: build_min
	docker compose -f ${MINIMAL} up

build_min:
	docker compose -f ${MINIMAL} build

py: py_build
	docker compose -f ${MINIMAL_PY} up

py_build:
	docker compose -f ${MINIMAL_PY} build

main: build_main
	docker compose -f ${STANDALONE} up

build_main:
	docker compose -f ${STANDALONE} build

symlink:
	ln -sf ${PWD}/${ACTION_FILE} ${PWD}/${DASHBOARD_DATA}/${ACTION_FILE}
