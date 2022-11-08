import React from 'react';
import './App.css';
import { fetchEventSource } from '@microsoft/fetch-event-source';

const url = "http://localhost:8000/";
const key_expression = "Genotyper/1/DNASensor/1/";

enum Endpoint {
    Health = "health"
}

const endpoint = (endpoint_name: Endpoint) => {
    return url + key_expression + endpoint_name;
}

await fetchEventSource(endpoint(Endpoint.Health), {
    method: "POST",
    headers: {
        Accept: "text/event-stream",
    },
    onopen(res: Response): any {
        if (res.ok && res.status === 200) {
            console.log("Connection made ", res);
          } else if (
            res.status >= 400 &&
            res.status < 500 &&
            res.status !== 429
          ) {
            console.log("Client side error ", res);
          }

    },
    onmessage(event: any) {
        console.log(`{event}`);
    },
    onerror(err: any) {
        console.error(`ERROR: {err}`);
    }
});

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>
          Simple Dashboard
        </h1>
      </header>
    </div>

  );
}

export default App;
