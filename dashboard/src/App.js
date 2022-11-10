import { useState, useEffect } from "react";
import './App.css';
import axios from 'axios';
import { ToastContainer, Flip, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import action from "./data/action.json";

const url = action.base_url;
const key_expression = action.key_expression;

function endpoint_url(endpoint = "") {
    return `${url}/${key_expression}/${endpoint.toLowerCase()}`;
}

const status_url = endpoint_url("status");

const actionServerActions = new Set(action.actions.map(item => item.name));

const HealthPlot = () => {
    let [actionStatus, setStatus] = useState("Unknown");

    useEffect(() => {
        const sse = new EventSource(status_url);

        sse.addEventListener("PUT", (e) => {
            const value = JSON.parse(e.data).value;
            console.log(value);
            setStatus(value); 
        });
    });

    const postAction = async action => {
        if (actionServerActions.has(action)) {
            try {
                const response = await axios.post(endpoint_url(action));
                toast.success(`Action dispatched: ${action}`);
                return response.data;
            } catch (error) {
                toast.error(error.message);
                throw error;
            } 
        } else {
            toast.error(`Action(${action}) not supported.`);
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
            newestOnTop={false}
            pauseOnHover={false}
        />
        <HealthPlot />
    </div>
  );
}

export default App;
