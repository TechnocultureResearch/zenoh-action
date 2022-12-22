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
          child_transition += transitionToStr(transition, cluster);
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
      return `${stateInitial} -> ${_stateInitial} [label="${transition.trigger}", lhead="cluster_${clusterLabel}", ltail="cluster_${_clusterLabel}", minlen=5]\n`;
    } else if (clusters.includes(transition.source)) {
      json.states.forEach((state) => {
        if (state.name === transition.source) {
          _stateInitial = state.initial;
          stateInitial += state.name;
        }
      });
      return `${_stateInitial} -> ${transition.dest} [label="${transition.trigger}", lhead="${transition.dest}", ltail="cluster_${stateInitial}", minlen=4]\n`;
    } else if (clusters.includes(transition.dest)) {
      json.states.forEach((state) => {
        if (state.name === transition.dest) {
          _stateInitial = state.initial;
          stateInitial += state.name;
        }
      });
      return `${transition.source} -> ${_stateInitial} [label="${transition.trigger}", lhead="cluster_${transition.dest}", ltail="${stateInitial}", minlen=4]\n`;
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

  dot += `Entry [shape="point" label=""]\n`;
  dot += `Entry -> ${json.initial}\n`;
  dot += `final[shape="doublecircle", label=""]\n`;
  if (currentState !== "") {
    dot += `${_currentState} [shape=ellipse, color=lightsalmon, fillcolor=lightsalmon,fontcolor=black, style=filled]; \n`;
  }

  let state_dict = states(json);
  let transition_list = transitions(json);

  console.log(state_dict);
  console.log(transition_list);

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
  return dot;
}
export default generateDotFile;
