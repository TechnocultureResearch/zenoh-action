import { useState, useEffect } from "react";
import './App.css';
import { ToastContainer, Flip, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const url = "http://localhost:8000";
const key_expression = "Genotyper/1/DNASensor/1";

function endpoint_url(endpoint = "") {
    return `${url}/${key_expression}/${endpoint.toLowerCase()}`;
}

const status_url = endpoint_url("status");

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

    function sendAction(actionString) {
        // Some code ...
        // What should be done when an action is to be dispatched
        // do a fetch POST/PUT request
        if (actionString === "start" || actionString === "stop") {
            fetch(endpoint_url(actionString), {
                method: 'PUT',
                headers: { 'Content-Type': 'text/plain' }
            });
            toast.info(`Action sent: ${actionString}`);
        } else {
            console.error(`Not a valid action string: ${actionString}`);
        }
    }

    return (
        <div>
            <h3>Status</h3>
            <p>{actionStatus}</p>

            <h3>Action Buttons</h3>
            <button onClick={() => sendAction("start")}>Start</button>
            <button onClick={() => sendAction("stop")}>Stop</button>
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
