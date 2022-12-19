import { useState, useEffect } from "react";
import './App.css';
import axios from 'axios';
import { ToastContainer, Flip, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Graphviz from 'graphviz-react';

import action from "./data/action.json";
import generateDotFile from "./data/generateDotFile";

const endpointsList = new Set(["trigger", "statechart", "state"]);

const url = action.base_url;
const key_expression = action.key_expression;

let chart = generateDotFile({});
console.log(chart)
const getStatechart = async () => {
    try {
        const response = await axios.get(endpoint_url("statechart"));
        const dot = generateDotFile(response.data[0].value.message);
        return [response.data[0].value.message, dot];

    } catch (error) {
        toast.error(error.message);
        throw error;
    }
};

const fetchStatechart = async () => {
    const [json, dot] = await getStatechart(); 
    chart = dot;
    console.log(chart)
};

function endpoint_url(endpoint = "") {
    let _endpoint = endpoint.split("?")[0] || endpoint;

    if (_endpoint === "") {
        return `${url}/${key_expression}`;
    } else if (!endpointsList.has(_endpoint)) {
        throw TypeError(`Endpoint(${_endpoint}) is not acceptable.`);
    }

    return `${url}/${key_expression}/${endpoint}`;
}


const ActionComponent = () => {
    let [currentState, setState] = useState("Unknown");
    //let chart = generateDotFile({});
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
            toast.success(`Action dispatched: ${action}\n${response.data}`);

            if (handler) {
                handler(response.data[0]);
            }

        } catch (error) {
            toast.error(error.message);
            throw error;
        }
    };

    let currentTime = Math.floor(Date.now() / 1000);
    
    return (
        <div>
            <h3>Status</h3>
            <p>{ currentState }</p>

            <h3>Action Buttons</h3>
            <button onClick={ () => postAction(`trigger?timestamp=${currentTime}&event=start`) }>Start</button>
            <button onClick={ () => postAction(`trigger?timestamp=${currentTime}&event=abort`) }>Stop</button>
            <button onClick={ () => postAction('state', setState) }>State</button>
            <button onClick={ () => fetchStatechart()}>Statechart</button>
            <Graphviz dot={ chart } options={{ fit: true }} />
            
        </div>
    );
};

function App(){

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
            <ActionComponent />
            
        </div>
    );
}

export default App;
