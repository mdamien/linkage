import React from 'react';
import ReactDOM from 'react-dom';

import { hashedColor } from './utils';

var ColorSquare = color => <span className='label' style={{ backgroundColor: color, marginRight: 10 }}> </span>;

/*
  params = {title, is_node, topics, renderer}
*/
function render(params) {
  var popup = <div></div>;
  if (params.title || (params.topics && params.topics.length > 0)) {
    popup = <div
        className="alert alert-dismissible alert-info"
        style={{ position: 'absolute', top: 10, right: 10, width: '40%'}}>
      <button type="button" className="close" onClick={() => render()}>&times;</button>
      {params.title}
      {params.cluster ? <p> - {ColorSquare(hashedColor(params.cluster))} {params.cluster}</p> : null}
      {params.topics && params.topics.length > 0 ? <div>
        Topics:
        <ul>
        {params.topics.map((v, i) => <li key={i}>{i}: {v.toFixed(2)} %</li>)}
        </ul>
      </div> : null}
    </div>;
  }

  var buttons = <div style={{ position: 'absolute', bottom: 10, right: 10}}>
    <button className="btn btn-primary btn-xs" onClick={() => params.renderer.resume()}>resume auto-layout</button>
    &nbsp;
    <button href="#" className="btn btn-primary btn-xs" onClick={() => params.renderer.pause()}>pause auto-layout</button>
    &nbsp;
    <button href="#" className="btn btn-primary btn-xs" onClick={() => params.expand_clusters()}>expand clusters</button>
    &nbsp;
    <button href="#" className="btn btn-primary btn-xs" onClick={() => params.collapse_clusters()}>collapse clusters</button>
  </div>;

  ReactDOM.render(<div>{buttons}{popup}</div>, document.getElementById('_graph-sidebar'));
};

export default render;