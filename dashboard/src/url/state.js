import React from 'react';
import { interpret } from 'xstate';
import { StateMachine } from '../statechart.json';

class statemachine extends React.Component {
  state = {
    current: StateMachine.initial
  };

  service = interpret(StateMachine).onTransition((current) =>
    this.setState({ current })
  );

  componentDidMount() {
    this.service.start();
  }

  componentWillUnmount() {
    this.service.stop();
  }

  render() {
    const { current } = this.state;
    const { send } = this.service;

    return (
      <button onClick={() => send('statemachine')}>
        {current.matches('busy') ? 'Subscribe' : 'Not Subscribe'}
      </button>
    );
  }
}
