import React from 'react';
import ReactDOM from 'react-dom';

function render(label) {
  var output = <div></div>;
  if (label) {
    output = <div
        className="alert alert-dismissible alert-info"
        style={{ position: 'absolute', top: 0, right: 0, maxWidth: '20%'}}>
      <button type="button" className="close" onClick={() => render()}>&times;</button>
      {label}
    </div>;
  }

  ReactDOM.render(output, document.getElementById('_graph-sidebar'));
};

export default render;