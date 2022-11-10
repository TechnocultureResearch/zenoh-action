COMPOSE_DIR:=test

MINIMAL:=${COMPOSE_DIR}/minimal.yml
STANDALONE:=${COMPOSE_DIR}/standalone.yml

ACTION_FILE:=action.json
DASHBOARD_DATA:=dashboard/src/data

dash: symlink
	docker compose -f ${MINIMAL} up

buildmin: symlink
	docker compose -f ${MINIMAL} build

standalone: symlink
	docker compose -f ${STANDALONE} up

build: symlink
	docker compose -f ${STANDALONE} build

symlink:
	ln -sf ${PWD}/${ACTION_FILE} ${PWD}/${DASHBOARD_DATA}/${ACTION_FILE}
