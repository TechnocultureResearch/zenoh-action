import { useState, useEffect } from "react";
import './App.css';
import axios from 'axios';
import { ToastContainer, Flip, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Graphviz from 'graphviz-react';

import action from "./data/action.json";

const endpointsList = new Set(["trigger", "statechart", "state"]);

const url = action.base_url;
const key_expression = action.key_expression;

function endpoint_url(endpoint = "") {
    let _endpoint = endpoint.split("?")[0] || endpoint;

    if (_endpoint === "") {
        return `${url}/${key_expression}`;
    } else if (!endpointsList.has(_endpoint)) {
        throw TypeError(`Endpoint(${_endpoint}) is not acceptable.`);
    }

    return `${url}/${key_expression}/${endpoint}`;
}

const ActionComponent = (statechart, setStatechart) => {
    let [currentState, setState] = useState("Unknown");

    useEffect(() => {
        const sse = new EventSource(endpoint_url("state"));

        sse.addEventListener("PUT", (e) => {
            const value = JSON.parse(e.data).value;
            if (value !== currentState) {
                setState(value);
            }
        });
    });

    const postAction = async (action, handler = () => { }) => {
        try {
            const response = await axios.get(endpoint_url(action));
            console.log(response.data[0].value)
            toast.success(`Action dispatched: ${action}\n${response.data}`);

            if (handler) {
                handler(response.data[0]);
            }

        } catch (error) {
            toast.error(error.message);
            throw error;
        }
    };
    const getStatechart = async (setStatechart, currentState) => {
        try {
            const response = await axios.get(endpoint_url("statechart"));
            console.log(response.data[0].value);
            setStatechart(generateDotFile(response.data[0].value, currentState));
        } catch (error) {
            toast.error(error.message);
            throw error;
        }
    };

    return (
        <div>
            <h3>Status</h3>
            <p>{ currentState }</p>

            <h3>Action Buttons</h3>
            <button onClick={ () => postAction(`trigger?timestamp=${Date.now()}&event=start`) }>Start</button>
            <button onClick={ () => postAction(`trigger?timestamp=${Date.now()}&event=abort`) }>Stop</button>
            <button onClick={ () => postAction('state', setState) }>State</button>
            <button onClick={ () => getStatechart(statechart, setStatechart) }>Statechart</button>
        </div>
    );
};


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

function App() {
    const [statechart, setStatechart] = useState({});
    const dot = generateDotFile(statechart, "idle");
    return (
        <div className="App">
            <header className="App-header">
                <h1>Action Dashboard</h1>
                <h3>Action Endpoint</h3>
                <p>{ endpoint_url() }</p>
            </header>

            <ToastContainer
                autoClose={ 1000 }
                transition={ Flip }
                hideProgressBar={ false }
                pauseOnFocusLoss={ false }
                newestOnTop={ true }
                pauseOnHover={ false }
            />
            <ActionComponent statechart={ statechart } setStatechart={ setStatechart } />
            <Graphviz dot = {dot} options={ { width: 1000, height: 1000 } } />
        </div>
    );
}

export default App;
