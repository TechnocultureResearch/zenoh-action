
const jsonToEventMap = (jsonStr) =>{
    var eventMap = {};
    var key = jsonStr.source + "," + jsonStr.dest;
    eventMap[key] = jsonStr.trigger;
    return eventMap;
  }

  let array = [];
const jsonToDict = (jsonStr) => {
let dict = {};
array.push(jsonStr.transitions)
for(let i=0; i<jsonStr.states.length; i++){
    let state = jsonStr.states[i];
    if (state.hasOwnProperty('transitions')){
        array.push(state.transitions);
    }
    if(state.children){
        for(let i=0; i<state.children.length; i++){
            let child = state.children[i];
            if (child.hasOwnProperty('transitions')){
                array.push(child.transitions);
            }
            if(child.children){
                for(let i=0; i<child.children.length; i++){
                    let child1 = child.children[i];
                    if (child1.hasOwnProperty('transitions')){
                        array.push(child1.transitions);
                    }
                }
            }
        }
    }
}
var array1d = [].concat(...array);
for(let i=0; i<array1d.length; i++){
    var key = [array1d[i].source, array1d[i].dest];
    dict[key] = array1d[i].trigger;
}
    return dict;
}

var data = {
    "before_state_change": [],
    "after_state_change": [],
    "prepare_event": [],
    "finalize_event": [],
    "send_event": true,
    "auto_transitions": true,
    "ignore_invalid_triggers": null,
    "queued": false,
    "models": [
       {
          "state": "idle",
          "name": "",
          "class-name": "self"
       }
    ],
    "initial": "idle",
    "transitions": [
       {
          "source": "idle",
          "dest": "healthy",
          "trigger": "start"
       },
       {
          "source": "healthy",
          "dest": "unhealthy",
          "trigger": "abort"
       },
       {
          "source": "healthy",
          "dest": "unhealthy",
          "trigger": "clearancetimeout"
       }
    ],
    "states": [
       {
          "name": "idle"
       },
       {
          "name": "healthy",
          "initial": "busy",
          "transitions": [
             {
                "source": "busy",
                "dest": "done",
                "trigger": "done"
             },
             {
                "source": "done",
                "dest": "awaitingclearance",
                "trigger": "awaitingclearance"
             },
             {
                "source": "awaitingclearance",
                "dest": "idle",
                "trigger": "idle"
             }
          ],
          "children": [
             {
                "name": "busy"
             },
             {
                "name": "done"
             },
             {
                "name": "awaitingclearance"
             },
             {
                "name": "unhealthy",
                "initial": "awaitingclearanceerr",
                "transitions": [
                   {
                      "source": "awaitingclearanceerr",
                      "dest": "cleared",
                      "trigger": "cleared"
                   },
                   {
                      "source": "cleared",
                      "dest": "brokenwithoutholdings",
                      "trigger": "brokenwithoutholdings"
                   },
                   {
                      "source": "awaitingclearanceerr",
                      "dest": "brokenwithholdings",
                      "trigger": "brokenwithholdings"
                   },
                   {
                      "source": "interalbrokenwithholdings",
                      "dest": "dead",
                      "trigger": "dead"
                   },
                   {
                      "source": "brokenwithoutholdings",
                      "dest": "dead",
                      "trigger": "dead"
                   }
                ],
                "children": [
                   {
                      "name": "awaitingclearanceerr"
                   },
                   {
                      "name": "cleared"
                   },
                   {
                      "name": "brokenwithholdings"
                   },
                   {
                      "name": "brokenwithoutholdings"
                   },
                   {
                      "name": "dead"
                   }
                ]
             }
          ]
       },
       {
          "name": "unhealthy",
          "initial": "awaitingclearanceerr",
          "transitions": [
             {
                "source": "awaitingclearanceerr",
                "dest": "cleared",
                "trigger": "cleared"
             },
             {
                "source": "cleared",
                "dest": "brokenwithoutholdings",
                "trigger": "brokenwithoutholdings"
             },
             {
                "source": "awaitingclearanceerr",
                "dest": "brokenwithholdings",
                "trigger": "brokenwithholdings"
             },
             {
                "source": "brokenwithholdings",
                "dest": "dead",
                "trigger": "dead"
             },
             {
                "source": "brokenwithoutholdings",
                "dest": "dead",
                "trigger": "dead"
             }
          ],
          "children": [
             {
                "name": "awaitingclearanceerr"
             },
             {
                "name": "cleared"
             },
             {
                "name": "brokenwithholdings"
             },
             {
                "name": "brokenwithoutholdings"
             },
             {
                "name": "dead"
             }
          ]
       }
    ]
 }

//console.log(jsonToDict(data));


// convert json to dot
const jsonToDot = (jsonStr) => {

    let dot = "digraph finite_state_machine {";
    dot += "rankdir=LR;";
    dot += "size=\"8,5\"";
    dot += "node [shape = doublecircle]; " + jsonStr.initial + ";";
    dot += "node [shape = circle];";
    dot += jsonStr.initial + " -> " + jsonStr.initial + ";";
    for(let i=0; i<jsonStr.states.length; i++){
        let state = jsonStr.states[i];
        if (state.hasOwnProperty('transitions')){
            for(let i=0; i<jsonStr.transitions.length; i++){
    
                let transition = jsonStr.transitions[i];
                dot += transition.source + " -> " + transition.dest + " [ label = \"" + transition.trigger + "\" ];";
            }
        }
        if(state.children){
            for(let i=0; i<state.children.length; i++){
                let child = state.children[i];
                if (child.hasOwnProperty('transitions')){
                    for(let i=0; i<jsonStr.transitions.length; i++){
    
                        let transition = jsonStr.transitions[i];
                        dot += transition.source + " -> " + transition.dest + " [ label = \"" + transition.trigger + "\" ];";
                    }
                }
                if(child.children){
                    for(let i=0; i<child.children.length; i++){
                        let child1 = child.children[i];
                        if (child1.hasOwnProperty('transitions')){
                            for(let i=0; i<jsonStr.transitions.length; i++){
    
                                let transition = jsonStr.transitions[i];
                                dot += transition.source + " -> " + transition.dest + " [ label = \"" + transition.trigger + "\" ];";
                            }
                        }
                    }
                }
            }
        }
    }
    for(let i=0; i<jsonStr.transitions.length; i++){
    
        let transition = jsonStr.transitions[i];
        dot += '{' + transition.source + " -> " + transition.dest + " [ label = \"" + transition.trigger + "\" ]; }";
    }
    return dot
    }


function str(transition){
   
   return `"${transition.source}" -> "${transition.dest}" [label="${transition.trigger}"]\n`;
}
cluster = ['healthy']
transition = {}
let dot = "hii"
for (let i=0; i<data.states.length;i++){
      if(cluster[0]==data.states[i].name){
         data.states[i].transitions.map(transition => {
            dot += str(transition);
         });
      }
   }
console.log(dot)