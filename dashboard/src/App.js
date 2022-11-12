import { useState, useEffect } from "react";
import './App.css';
import axios from 'axios';
import { ToastContainer, Flip, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import action from "./data/action.json";

const actionsList = new Set(action.actions);
const statesList = new Set(action.states);
const endpointsList = new Set([...actionsList, ...statesList, "connect"]);

const url = action.base_url;
const key_expression = action.key_expression;

function endpoint_url(endpoint = "") {
    if (endpointsList.has(endpoint)) {
        return `${url}/${key_expression}/${endpoint}`;
    } else if (endpoint === "") {
        return `${url}/${key_expression}`;
    } else {
        throw TypeError(`Declaration for Endpoint(${endpoint}) is not present in the action.json file`);
    }
}

const ActionComponent = () => {
    let [actionStatus, setStatus] = useState("Unknown");

    useEffect(() => {
        const sse = new EventSource(endpoint_url("connect"));

        sse.addEventListener("PUT", (e) => {
            const value = JSON.parse(e.data).value;
            if (value !== actionStatus) {
                setStatus(value); 
            }
        });
    });

    const postAction = async action => {
        if (actionsList.has(action)) {
            try {
                const response = await axios.post(endpoint_url(action));
                toast.success(`Action dispatched: ${action}`);
                return response.data;
            } catch (error) {
                toast.error(error.message);
                throw error;
            } 
        } else {
            const errmsg = `Action(${action}) not supported.`;
            toast.error(errmsg);
            throw errmsg;
        }
    };

    return (
        <div>
            <h3>Status</h3>
            <p>{actionStatus}</p>

            <h3>Action Buttons</h3>
            <button onClick={() => postAction("start")}>Start</button>
            <button onClick={() => postAction("stop")}>Stop</button>

            <button onClick={() => postAction("hello")}>Hello</button>
        </div>
    );
}

function App() {
  return (
    <div className="App">
        <header className="App-header">
            <h1>Action Dashboard</h1>
            <h3>Action Endpoint</h3>
            <p>{endpoint_url()}</p>
        </header>

        <ToastContainer 
            autoClose={1000}
            transition={Flip}
            hideProgressBar={false}
            pauseOnFocusLoss={false}
            newestOnTop={true}
            pauseOnHover={false}
        />
        <ActionComponent />
    </div>
  );
}

export default App;
