import React from 'react';
import ReactDOM from 'react-dom';

function render(label, topics = []) {
  var output = <div></div>;
  if (label || topics.length > 0) {
    output = <div
        className="alert alert-dismissible alert-info"
        style={{ position: 'absolute', top: 0, right: 0, width: '30%'}}>
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

  ReactDOM.render(output, document.getElementById('_graph-sidebar'));
};

export default render;