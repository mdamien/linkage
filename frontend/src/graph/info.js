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

class ClusterNodes extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        showAll: false,
      };
      this.toggleShow = this.toggleShow.bind(this);
    }
    toggleShow() {
        this.setState({showAll: !this.state.showAll});
    }
    render() {
        let {nodes} = this.props;
        const sorted_nodes = nodes.concat().sort();
        return <p>
            <p style={{marginTop: 10}}>
                <a className='btn btn-warning btn-xs' onClick={this.toggleShow}>
                  {this.state.showAll ? 'hide' : 'show'} all nodes
                </a>
            </p>
            {this.state.showAll ? <div>
              <h5>All nodes:</h5>
                <ul>
                    {sorted_nodes.map((t, i) => {
                      return <li key={i}>{t}</li>;
                    })}
                </ul>
              </div> : null}
        </p>
    }
}

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
        style={{ position: 'absolute', top: 10, right: 10, width: '40%', maxHeight: '70%', overflow: 'auto'}}>
      <button type="button" className="close" onClick={() => render({
        renderer: params.renderer,
        expand_clusters: params.expand_clusters,
        collapse_clusters: params.collapse_clusters,
      })}>&times;</button>
      {params.is_cluster ? <div>
        {ColorSquare(get_color(params.title, 'Paired'), params.cluster_label)}
        {USER_ID == GRAPH.user ? <button
          title='Edit cluster label'
          className='btn btn-xs btn-default btn-warning btn-toolbar'
          onClick={() => {
            var name = prompt('Choose a custom label for the cluster:');
            params.update_cluster_label(params.title, name);
            render(null);
          }}>
          <Icon name='pencil'/>
        </button> : null}
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
        <h4>Top nodes:</h4>
        <ul>
        {params.top_nodes.slice(0, 5).map((v, i) => <li key={i}>
          {v}
        </li>
        )}
      </ul>
      <ClusterNodes nodes={params.top_nodes} />
      </div> : null}
    </div>;
  }

  ReactDOM.render(popup, document.getElementById('_graph-sidebar'));
};

export default render;
