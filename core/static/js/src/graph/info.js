import React from 'react';
import ReactDOM from 'react-dom';

function render(label, topics = [], renderer) {
  var popup = <div></div>;
  if (label || topics.length > 0) {
    popup = <div
        className="alert alert-dismissible alert-info"
        style={{ position: 'absolute', top: 10, right: 10, width: '30%'}}>
      <button type="button" className="close" onClick={() => render()}>&times;</button>
      {label}
      {topics.length > 0 ? <div>
        Topics:
        <ul>
        {topics.map((v, i) => <li key={i}>{i}: {v.toFixed(2)} %</li>)}
        </ul>
      </div> : null}
    </div>;
  }

  var buttons = <div style={{ position: 'absolute', top: 10, left: 10}}>
    <button className="btn btn-primary btn-xs" onClick={() => renderer.resume()}>resume</button>
    &nbsp;
    <button href="#" className="btn btn-primary btn-xs" onClick={() => renderer.pause()}>pause</button>
  </div>;

  ReactDOM.render(<div>{buttons}{popup}</div>, document.getElementById('_graph-sidebar'));
};

export default render;