FILE:=action.smcat

build:
	smcat -T png ${FILE}

dev:
	watchman watch ./
	watchman -- trigger ./ rebuild '*.smcat' -- smcat -T png ${FILE}
	#watchman -- trigger ./ rebuild '*.smcat' -- smcat -T scxml ${FILE}
	#watchman -- trigger ./ rebuild '*.smcat' -- smcat -T json ${FILE}
	#watchman -- trigger ./ rebuild '*.smcat' -- smcat -T scjson ${FILE}

clean:
	rm *.json *.scjson *.scxml *.png *.svg
