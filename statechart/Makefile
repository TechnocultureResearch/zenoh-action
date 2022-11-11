FILE:=action.smcat

dev:
	watchman watch ./
	watchman -- trigger ./ rebuild '*.smcat' -- smcat ${FILE}
