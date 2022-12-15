function states(json) {
    let _states = {};

    if (json.states === undefined) {
        return _states;
    }

    if (json.states === {}) {
        return _states;
    }

    json.states.forEach(state => {
        _states[state.name] = (state.children && state.children.length !== 0) || false;

        if (state.children) {
            state.children.forEach(child => {
                _states[child.name] = (child.children && child.children.length !== 0) || false;
            });
        }
    });

    return _states;
}

function transitions(json) {
    let _transitions = [];

    if (json.transitions === undefined || json.states === undefined) {
        return _transitions;
    }

    if (json.transitions === {} || json.states === {}) {
        return _transitions;
    }

    json.transitions.forEach(transition => {
        _transitions.push(transition);
    });

    json.states.forEach(state => {
        state.children && state.children.forEach(substate => {
            substate.transitions && substate.transitions.forEach(transition => {
                _transitions.push(transition);
            });
        });
    });

    // console.log(_transitions);
    return _transitions;
}

function childtransitionToStr(json, cluster) {
    let child_transition = "";
    json.states.forEach(state => {
        if (cluster === state.name) {
            state.transitions.forEach(transition => {
                child_transition += transitionToStr(transition, cluster);
            });
        }
    });
    return child_transition;
}

function transitionToStr(transition, state_list) {
    let cluster_label = "";
    if (state_list[transition.dest]) {
        cluster_label += `, ltail=${transition.dest}`;
    }
    if (state_list[transition.source]) {
        cluster_label += `, lhead=${transition.source}`;
    }
    return `"${transition.source}" -> "${transition.dest}" [label="${transition.trigger} ${cluster_label}"]\n`;
}

function generateDotFile(json, current_state) {
    let dot = "";

    if (json === undefined) {
        return dot;
    }

    dot += "digraph {\n";
    dot += `rankdir=LR;\n`;
    dot += `Entry [shape="point" label=""]`;
    dot += `Entry -> ${json.initial}\n`;
    dot += `${json.initial} [shape=ellipse, color=red, fillcolor= orangered3, fontcolor=black, style=filled]; \n`;

    // Approach 1: Build some data structures, then draw
    let state_dict = states(json);
    let transition_list = transitions(json);

    const clusters = [];
    Object.entries(state_dict)
        .filter(([k, v]) => v === true)
        .forEach(arr => clusters.push(arr[0]));


    clusters.forEach(cluster => {
        dot += `subgraph cluster_${cluster} {\n`;
        dot += `${current_state.split("_").pop()} [shape=ellipse, color=lightsalmon, fillcolor=lightsalmon, fontcolor=black, style=filled]; \n`;
        dot += childtransitionToStr(json, cluster);
        dot += ` label=${cluster}\n`;

        dot += `}\n`;
    });

    transition_list.forEach(transition => {
        dot += transitionToStr(transition, state_dict);
    });

    dot += "}\n";
    return dot;
}

export default generateDotFile;