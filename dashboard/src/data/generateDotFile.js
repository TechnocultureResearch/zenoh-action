import './App.css'
import Graphviz from 'graphviz-react';
import statechart from './statechart.json';

function states(json) {
	let _states = {};

	json.states.map(state => {
		_states[state.name] = (state.children && state.children.length != 0) || false;

		if (state.children) {
			state.children.map(child => {
				_states[child.name] = (child.children && child.children.length != 0) || false;
			});
		}
	});

	return _states;
}

function children_of(json, state) {
	return [];
}
function transitions(json) {
	let _transitions = [];

	json.transitions.map(transition => {
		_transitions.push(transition)
	})
/*
	json.states.map(state => {
		state.children && state.children.map(substate => {
			substate.transitions && substate.transitions.map(transition => {
				_transitions.push(transition)
			})
		})
	})*/

	// console.log(_transitions);
	return _transitions;
}

function childtransitionToStr(json, cluster) {
	let child_transition = "";
	json.states.map(state => {
		if (cluster == state.name) {
			state.transitions.map(transition => {
				child_transition += transitionToStr(transition, cluster);
			});
    }
  })
  console.log(`child transitions ${child_transition}`);
	return child_transition;
}

function transitionToStr(transition, state_list, clusters) {
	let cluster_label = "";
  if(clusters != undefined){
    console.log(clusters.includes(transition.source))
    if(clusters.includes(transition.source)){
      cluster_label += `, lhead=cluster_${transition.source}`;}
  }
  else if (state_list[transition.source]) {
		// console.log(`${transition.source} has children.`);
		cluster_label += `, lhead=${transition.source}`;
	}
  if(clusters != undefined){
    console.log(clusters.includes(transition.source))
    if(clusters.includes(transition.source)){
      cluster_label += `, ltail=cluster_${transition.dest}`;}
  }
	else if (state_list[transition.dest]) {
		// console.log(`${transition.dest} has children.`);
		cluster_label += `, ltail=${transition.dest}`;
	}
  
	return `"${transition.source}" -> "${transition.dest}" [label="${transition.trigger} ${cluster_label}"]\n`;
}

function generateDotFile(json, current_state) {
	let dot = "digraph {\n";
	dot += `rankdir=LR;\n`;
	dot += `Entry [shape="point" label=""]`;
	dot += `Entry -> ${json.initial}\n`;
  dot += `${json.initial} [shape=ellipse, color=red, fillcolor= orangered3, fontcolor=black, style=filled]; \n`;
  dot += `${current_state} [shape=ellipse, color=lightsalmon, fillcolor=lightsalmon, fontcolor=black, style=filled]; \n`;
	// Approach 1: Build some data structures, then draw
	let state_dict = states(statechart);
	let transition_list = transitions(statechart);

	console.log(state_dict)
	console.log(transition_list);

	const clusters = [];
	Object.entries(state_dict)
		.filter(([k, v]) => v === true)
		.map(arr => clusters.push(arr[0]));
	console.log(clusters);

	clusters.map(cluster => {
		dot += `subgraph cluster_${cluster} {\n`;
    json.states.map(state=>{
      if(state.name == cluster){
        console.log(state.inital)
      }
    })
		dot +=  childtransitionToStr(json, cluster);
		dot += ` label=${cluster}\n`;

		children_of(cluster).map(state => {
			dot += `  ${state}\n`;

		})

		dot += `}\n`;
	})

	transition_list.map(transition => {
		dot += transitionToStr(transition, state_dict, clusters);
	})

	// Approach 2: Draw while we parse
	// dot += subStates(json, "idle");

	dot += "}\n";
	return dot;
}
var current_state = "busy";
export default function App() {
	const dot = generateDotFile(statechart, current_state);
	console.log(dot)
	return (
		<div>
			<Graphviz dot={dot} />
			<p>{dot}</p>
		</div>
	);
}
