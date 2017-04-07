import React from 'react';
import ReactDOM from 'react-dom';

import { get_color, hashedColor } from './utils';

var ColorSquare = (color, content=<span>&nbsp;</span>, width='auto') => <span className='label' style={{
    backgroundColor: color,
    marginRight: 10,
    width: width,
    display: 'inline-block'
  }}>{content}</span>;

/*
  params = {title, is_node, topics, renderer}
*/
function render(params) {
  var popup = <div></div>;
  if (params.title !== undefined || (params.topics && params.topics.length > 0)) {
    popup = <div
        className="alert alert-dismissible alert-info"
        style={{ position: 'absolute', top: 10, right: 10, width: '40%'}}>
      <button type="button" className="close" onClick={() => render({
        renderer: params.renderer,
        expand_clusters: params.expand_clusters,
        collapse_clusters: params.collapse_clusters,
      })}>&times;</button>
      {params.is_cluster ? ColorSquare(get_color(params.title, 'Paired'), params.title) : params.title}
      {params.cluster !== undefined ? <p> - {ColorSquare(get_color(params.cluster, 'Paired'))} {params.cluster}</p> : null}
      {params.words && params.words.length > 0 ? <div>
        {params.words.slice(0, 10).map((v, i) => <span key={i}>
              <span className="label label-default">{v}</span>{' '}
            </span>
        )}
      </div> : null}
      {params.topics && params.topics.length > 0 ? <div>
        <h4>Topics</h4>
        {params.topics.map((v, i) => <div key={i}>
          {ColorSquare(get_color(i), v > 0.20 ? params.topicsName[i] : <span>&nbsp;</span>,
              (v * 100).toFixed(2) + '%')}&nbsp;{(v * 100).toFixed(1)}&nbsp;%
        </div>)}
      </div> : null}
      {params.top_nodes && params.top_nodes.length > 0 ? <div>
        <br/>
        <h4>Sample of nodes</h4>
        <ul>
        {params.top_nodes.map((v, i) => <li key={i}>
          {v}
        </li>)}
        </ul>
      </div> : null}
    </div>;
  }

  var buttons = <div style={{ position: 'absolute', bottom: 10, right: 10}}>
    <button className="btn btn-primary btn-xs" onClick={() => params.renderer.clear_pause_in()}>resume auto-layout</button>
    &nbsp;
    <button href="#" className="btn btn-primary btn-xs" onClick={() => params.renderer.pause_in(0)}>pause auto-layout</button>
    &nbsp;
    <button href="#" className="btn btn-primary btn-xs" onClick={() => params.expand_clusters()}>expand clusters</button>
    &nbsp;
    <button href="#" className="btn btn-primary btn-xs" onClick={() => params.collapse_clusters()}>collapse clusters</button>
  </div>;

  ReactDOM.render(<div>{buttons}{popup}</div>, document.getElementById('_graph-sidebar'));
};

export default render;
