function connectedStatesList(json, _states) {
  let connectedStates = {};
  let _connected = [];
  Object.entries(_states)
    .filter(([k, v]) => v === false)
    .map((arr) => {
      json.states.map((state) => {
        if (state.transitions) {
          state.transitions.map((transition) => {
            if (transition.source == arr[0]) {
              _connected.push(transition.dest);
            }
          });
        }
      });
      connectedStates[arr[0]] = _connected;
      _connected = [];
    });
  let keys = Object.keys(connectedStates);
  json.states.map((state) => {
    json.transitions.map((transition) => {
      if (transition.source == state.name) {
        if (keys.includes(state.name))
          connectedStates[state.name].push(transition.dest);
        else {
          _connected.push(transition.dest);
        }
      }
    });
    connectedStates[state.name] = _connected;
    _connected = [];
  });
  console.log(connectedStates);
}

function states(json) {
  let _states = {};

  json.states.forEach((state) => {
    _states[state.name] =
      (state.children && state.children.length !== 0) || false;

    if (state.children) {
      state.children.forEach((child) => {
        _states[child.name] =
          (child.children && child.children.length !== 0) || false;
      });
    }
  });

  return _states;
}

function transitions(json) {
  let _transitions = [];

  json.transitions.forEach((transition) => {
    _transitions.push(transition);
  });
  return _transitions;
}

function childtransitionToStr(json, cluster) {
  let child_transition = "";
  let transition_ = "";
  json.states.forEach((state) => {
    if (cluster === state.name) {
      state.transitions.forEach((transition) => {
        if (transition.dest === "final") {
          transition_ = `${transition.source} -> final_${cluster};`;
          child_transition += transition_;
        } else {
          child_transition += transitionToStr(transition);
        }
      });
    }
  });
  return child_transition;
}

function transitionToStr(transition, json, clusters) {
  let clusterLabel = "";
  let _clusterLabel = "";
  let stateInitial = "";
  let _stateInitial = "";
  let label = "";
  if (clusters !== undefined) {
    if (
      clusters.includes(transition.source) &&
      clusters.includes(transition.dest)
    ) {
      json.states.forEach((state) => {
        if (state.name === transition.source) {
          if (state.initial === undefined) {
            stateInitial += state.name;
          } else {
            stateInitial += state.initial;
          }
          clusterLabel += state.name;
        }
        if (state.name === transition.dest) {
          if (state.name === undefined) {
            _stateInitial += state.name;
          } else {
            _stateInitial += state.initial;
          }
          _clusterLabel += state.name;
        }
      });
      return `${stateInitial} -> ${_stateInitial} [label="${transition.trigger}", lhead="cluster_${_clusterLabel}", ltail="cluster_${clusterLabel}", minlen=5]\n`;
    } else if (clusters.includes(transition.source)) {
      json.states.forEach((state) => {
        if (state.name === transition.source) {
          _stateInitial = state.initial;
          stateInitial += state.name;
          if (transition.dest === "final") {
            label = "";
          } else {
            label = transition.trigger;
          }
        }
      });
      return `${_stateInitial} -> ${transition.dest} [label="${label}", lhead="${transition.dest}", ltail="cluster_${stateInitial}", minlen=4]\n`;
    } else if (clusters.includes(transition.dest)) {
      json.states.forEach((state) => {
        if (state.name === transition.dest) {
          _stateInitial = state.initial;
          stateInitial += state.name;
        }
      });
      return `${transition.source} -> ${_stateInitial} [label="${transition.trigger}", lhead=cluster_${transition.dest}, ltail="${stateInitial}", minlen=4]\n`;
    }
  } else {
    return `"${transition.source}" -> "${transition.dest}" [label="${transition.trigger}"]\n`;
  }
}

function generateDotFile(json, currentState = "") {
  let dot = "";
  dot += "digraph {\n";
  dot += `rankdir=TD;\n`;

  let _currentState = currentState.split("_").pop() || currentState;

  if (json === undefined) {
    dot += "}";
    return dot;
  }

  if (Object.keys(json).length === 0) {
    dot += "}";
    return dot;
  }
  dot += `compound=True;\n`;
  dot += `Entry [shape="point" label=""]\n`;
  dot += `Entry -> ${json.initial}\n`;
  dot += `final[shape="doublecircle", label=""]\n`;
  if (currentState !== "") {
    dot += `${_currentState} [shape=ellipse, color=lightsalmon, fillcolor=lightsalmon,fontcolor=black, style=filled]; \n`;
  }

  let state_dict = states(json);
  let transition_list = transitions(json);

  const clusters = [];
  Object.entries(state_dict)
    .filter(([k, v]) => v === true)
    .forEach((arr) => clusters.push(arr[0]));

  clusters.forEach((cluster) => {
    dot += `subgraph cluster_${cluster} {\n`;
    dot += ` label=${cluster}\n`;
    dot += `final_${cluster}[label="", shape="doublecircle"]\n`;
    json.states.forEach((state) => {
      if (state.name === cluster) {
        dot += `entry_${cluster}[label="", shape="point"]\n`;
        dot += `entry_${cluster} -> ${state.initial}\n`;
      }
    });
    dot += childtransitionToStr(json, cluster);

    dot += `}\n`;
  });

  transition_list.forEach((transition) => {
    dot += transitionToStr(transition, json, clusters);
  });

  dot += "}\n";
  console.log(dot);
  connectedStatesList(json, state_dict);
  return dot;
}

export default generateDotFile;
export { connectedStatesList, states, transitions, childtransitionToStr, transitionToStr };