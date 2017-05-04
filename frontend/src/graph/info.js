import React from 'react';
import ReactDOM from 'react-dom';

import { get_color, hashedColor } from './utils';

var ColorSquare = (color, content=<span>&nbsp;</span>, width='auto') => <span className='label' style={{
    backgroundColor: color,
    marginRight: 10,
    width: width,
    display: 'inline-block'
  }}>{content}</span>;

const Icon = props => <span className={'glyphicon glyphicon-' + props.name}></span>;

/*
  params = {title, is_node, topics, renderer}
*/
function render(params) {
  if (params === null) {
    ReactDOM.render(<div></div>, document.getElementById('_graph-sidebar'));
    return;
  }
  var popup = <div></div>;
  if (params.title !== undefined || (params.topics && params.topics.length > 0)) {
    popup = <div
        className="alert alert-dismissible alert-info"
        style={{ position: 'absolute', top: 10, right: 10, width: '40%', maxHeight: 300, overflow: 'auto'}}>
      <button type="button" className="close" onClick={() => render({
        renderer: params.renderer,
        expand_clusters: params.expand_clusters,
        collapse_clusters: params.collapse_clusters,
      })}>&times;</button>
      {params.is_cluster ? <div>
        {ColorSquare(get_color(params.title, 'Paired'), params.cluster_label)}
        <button
          title='Edit cluster label'
          className='btn btn-xs btn-default btn-warning btn-toolbar'
          onClick={() => {
            var name = prompt('Choose a custom label for the cluster:');
            params.update_cluster_label(params.title, name);
            render(null);
          }}>
          <Icon name='pencil'/>
        </button>
      </div> : params.title}
      {params.cluster !== undefined ? <p> - {ColorSquare(get_color(params.cluster, 'Paired'))} {params.cluster}</p> : null}
      {params.words && params.words.length > 0 ? <div>
        {params.words.slice(0, 10).map((v, i) => <span key={i}>
              <span className="label label-default">{v}</span>{' '}
            </span>
        )}
      </div> : null}
      {params.pi_value ? <p><abbr title="cluster-to-cluster relationship">PI</abbr>: {(params.pi_value*100).toFixed(4)} %</p> : null}
      {params.topics && params.topics.length > 0 ? <div>
        <h4>Topics</h4>
        {params.topics.map((v, i) => <div key={i}>
          {ColorSquare(get_color(i), v > 0.20 ? params.topicsName[i] : <span>&nbsp;</span>,
              (v * 100).toFixed(2) + '%')}&nbsp;{(v * 100).toFixed(1)}&nbsp;%
        </div>)}
      </div> : null}
      {params.top_nodes && params.top_nodes.length > 0 ? <div>
        <br/>
        <h4>Nodes</h4>
        <ul>
        {params.top_nodes.map((v, i) => <li key={i}>
          {v}
        </li>)}
        </ul>
      </div> : null}
    </div>;
  }

  ReactDOM.render(popup, document.getElementById('_graph-sidebar'));
};

export default render;
