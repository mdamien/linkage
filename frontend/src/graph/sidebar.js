import React from 'react';
import ReactDOM from 'react-dom';
import Slider from 'rc-slider';
import Tooltip from 'rc-tooltip';

import Autocomplete from 'react-autocomplete'

import { get_color, hashedColor, n_best_elems } from './utils';
import { init, display_loading, zoom_on } from '../graph';

var ColorSquare = (color, content=' ')  => <span className='label' style={{ backgroundColor: color, marginRight: 10 }}>{content}</span>;

const Icon = props => <span className={'glyphicon glyphicon-' + props.name}></span>;

function sortStates (a, b, value) {
  return (
    a.toLowerCase().indexOf(value.toLowerCase()) >
    b.toLowerCase().indexOf(value.toLowerCase()) ? 1 : -1
  )
}

const searchStyles = {
  item: {
    padding: '2px 6px',
    cursor: 'default'
  },

  highlightedItem: {
    color: 'white',
    background: 'hsl(200, 50%, 50%)',
    padding: '2px 6px',
    cursor: 'default'
  },

  menu: {
    border: 'solid 1px #ccc'
  }
}

let SearchBar = React.createClass({
  getInitialState() {
    return { value: '' }
  },
  render () {
    return (
      <div className='panel panel-default panel-body'>
        <label htmlFor="states-autocomplete">Search</label><br/>
        <Autocomplete
          value={this.state.value}
          inputProps={{name: "US state", id: "states-autocomplete"}}
          items={this.props.choices}
          className='form-control'
          getItemValue={(item) => item}
          shouldItemRender={(item, value) => 
            item.toLowerCase().indexOf(value.toLowerCase()) !== -1
          }
          onChange={(event, value) => this.setState({ value })}
          onSelect={value => {
            this.setState({ value });
            this.props.onSelect(value);
          }}
          renderItem={(item, isHighlighted) => (
            <div
              style={isHighlighted ? searchStyles.highlightedItem : searchStyles.item}
              key={item}
            >{item}</div>
          )}
          menuStyle={{
              borderRadius: '3px',
              boxShadow: '0 2px 12px rgba(0, 0, 0, 0.1)',
              background: 'rgba(255, 255, 255, 0.9)',
              padding: '2px 0',
              fontSize: '90%',
              position: 'fixed',
              overflow: 'auto',
              maxHeight: '50%',
              zIndex: 100,
            }}
        />
      </div>
    )
  }
})

const EPS_TOPICS = 0.0000001;

class TopicWords extends React.Component {
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
        let {i, words, dictionnary, nodes_meta, update_topic_name} = this.props;
        var best5 = n_best_elems(words, 5, v => v.tfidf);
        var label = dictionnary[best5[0][0]];
        var topic_meta = nodes_meta['t-' + i];
        if (topic_meta && topic_meta['label']) {
          label = topic_meta['label'];
        }
        return <div className='list-group-item'>
            <p>
              {ColorSquare(get_color(i), label)}
              {' '}
              {USER_ID == GRAPH.user ? <a
                title='Edit topic label'
                className='btn btn-warning btn-xs'
                onClick={() => {
                  var name = prompt('Choose a custom label for the topic:');
                  update_topic_name(i, name);
                }}>
                <Icon name='pencil'/>
              </a> : null}
            </p>
            ex: {best5.map((t, i) => {
                return <span key={i}>
                    <span
                        className="label label-default"
                    >{dictionnary[t[0]]}</span>{' '}
                </span>
            })}
            <p style={{marginTop: 10}}>
                <a className='btn btn-warning btn-xs' onClick={this.toggleShow}>
                  {this.state.showAll ? 'hide' : 'show'} words
                </a>
            </p>
            {this.state.showAll ? <table className='table table-striped table-bordered'>
                <tbody>
                    {n_best_elems(words, 1000, v => v.tfidf).map((t, i) => {
                      if (t[1].freq < EPS_TOPICS) return;
                      return <tr key={i}>
                          <td>{dictionnary[t[0]]}</td>
                          <td className='text-right'>{(t[1].freq * 100).toFixed(3)} %</td>
                          {/*<td className='text-right'>{(t[1].tfidf * 100).toFixed(2)}</td>*/}
                      </tr>;
                    })}
                </tbody>
            </table> : null}
        </div>
    }
};

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
        let {i, size, label, update_label} = this.props;
        let nodes = GRAPH.result.top_nodes[i];
        return <div className='list-group-item'>
            <p>
              {ColorSquare(get_color(i, 'Paired'), label ? (label + ' (' + size + ')') : size)}
              {' '}
              {USER_ID == GRAPH.user ? <a
                title='Edit cluster label'
                className='btn btn-warning btn-xs'
                onClick={() => {
                  var name = prompt('Choose a custom label for the cluster:');
                  update_label(i, name);
                }}>
                <Icon name='pencil'/>
              </a> : null}
            </p>
            <p style={{marginTop: 10}}>
                <a className='btn btn-warning btn-xs' onClick={this.toggleShow}>
                  {this.state.showAll ? 'hide' : 'show'} nodes
                </a>
            </p>
            {this.state.showAll ? <table className='table table-striped table-bordered'>
                <tbody>
                    {nodes.map((t, i) => {
                      return <tr key={i}>
                          <td>{t}</td>
                      </tr>;
                    })}
                </tbody>
            </table> : null}
        </div>
    }
};

const handle = (props) => {
  const { value, dragging, index } = props;
  delete props.dragging;
  delete props.value;
  delete props.index;
  return (
    <Tooltip
      prefixCls="rc-slider-tooltip"
      overlay={value}
      visible={dragging}
      placement="top"
      key={index}
    >
      <Slider.Handle {...props} />
    </Tooltip>
  );
};

class Sidebar extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        clusters: GRAPH.result ? GRAPH.result.param_clusters : 3,
        topics: GRAPH.result ? GRAPH.result.param_topics : 3,
        cutoff: GRAPH.cluster_to_cluster_cutoff * 100,
        tab: 'clustering',
      };
      this.updateClusters = this.updateClusters.bind(this);
      this.updateTopics = this.updateTopics.bind(this);
      this.updateCutoff = this.updateCutoff.bind(this);

      if (GRAPH.result) {
        this.props.state.current_selected_topics = this.state.topics;
        this.props.state.current_selected_clusters = this.state.clusters;
      }
    }
    updateClusters(clusters) {
        this.setState({clusters: clusters});
        $.post('/result/' + GRAPH.id + '/cluster_it/', {
            clusters: clusters,
            topics: this.state.topics,
        }, function(data) {
            console.log(data);
            if (data.result) {
              GRAPH.result = data.result
              init();
            }
        });
        this.props.state.current_selected_topics = this.state.topics;
        this.props.state.current_selected_clusters = clusters;
        display_loading();
    }
    updateTopics(topics) {
        this.setState({topics: topics});
        $.post('/result/' + GRAPH.id + '/cluster_it/', {
            clusters: this.state.clusters,
            topics: topics,
        }, function(data) {
            console.log(data);
            if (data.result) {
              GRAPH.result = data.result
              init();
            }
        });
        this.props.state.current_selected_topics = topics;
        this.props.state.current_selected_clusters = this.state.clusters;
        display_loading();
    }
    updateCutoff(cutoff) {
        this.setState({cutoff: cutoff});
        GRAPH.cluster_to_cluster_cutoff = cutoff / 100;
        init();
    }
    componentWillReceiveProps(props) {
      if (props.state.force_use_result_param) {
        this.setState({
            clusters: GRAPH.result.param_clusters,
            topics: GRAPH.result.param_topics,
        })
        props.state.force_use_result_param = false;
      }
    }
    render() {
        var state = this.props.state;

        var marks_clusters = {};
        marks_clusters[GRAPH.job_param_clusters] = GRAPH.job_param_clusters;
        marks_clusters[GRAPH.job_param_clusters_max] = GRAPH.job_param_clusters_max;

        var marks_topics = {};
        marks_topics[GRAPH.job_param_topics] = GRAPH.job_param_topics;
        marks_topics[GRAPH.job_param_topics_max] = GRAPH.job_param_topics_max;

        return <div>
            {!GRAPH.magic_too_big_to_display_X ? <ul className="nav nav-tabs">
              <li className={this.state.tab == 'clustering' ? 'active' : ''}>
                <a href='#'
                  onClick={() => this.setState({tab: 'clustering'})}>
                    Clustering
                </a>
              </li>
              <li className={this.state.tab == 'advanced' ? 'active' : ''}>
                  <a href='#'
                    onClick={() => this.setState({tab: 'advanced'})}>
                      Advanced
                  </a>
              </li>
              {/*<li className={this.state.tab == 'log' ? 'active' : ''}>
                  <a href='#'
                    onClick={() => this.setState({tab: 'log'})}>
                      Log
                  </a>
              </li>*/}
            </ul> : null}
            {!GRAPH.magic_too_big_to_display_X ? <br/> : null}
            {this.state.tab == 'clustering' ?
              <div>
              {!state.meta_mode ? <SearchBar choices={state.labels}
                onSelect={value => zoom_on(state.labels.indexOf(value))}/> : null}
              <div className='panel panel-default'>
                  <div className='panel-heading'>
                      <h3 className='panel-title'>Topics 
                          {state.topicToTerms ?
                              <span> - {state.topicToTerms.length}</span>
                              : null}
                      </h3>
                  </div>
                  {GRAPH.job_param_topics != GRAPH.job_param_topics_max ? <div className='panel-body'>
                      <Slider steps={1} dots defaultValue={this.state.topics}
                        min={GRAPH.job_param_topics}
                        max={GRAPH.job_param_topics_max}
                        marks={marks_topics}
                        onAfterChange={this.updateTopics}/>
                      <br/>
                  </div> : null}
                  {state.topicToTermsTFIDF ? <div className='list-group'>
                      {state.topicToTermsTFIDF.map((v, i) => 
                          <TopicWords
                            words={v}
                            i={i}
                            key={i}
                            dictionnary={state.dictionnary}
                            nodes_meta={state.nodes_meta}
                            update_topic_name={state.update_topic_name}
                            />
                      )}
                  </div> : null}
              </div>
              <div className='panel panel-default'>
                  <div className='panel-heading'>
                      <h3 className='panel-title'>Clusters 
                          {state.clusterToNodes ?
                              <span> - {Object.keys(state.clusterToNodes).length}</span>
                              : null}
                      </h3>
                  </div>
                  {GRAPH.job_param_clusters != GRAPH.job_param_clusters_max ? <div className='panel-body'>
                      <Slider steps={1} dots defaultValue={this.state.clusters}
                        min={GRAPH.job_param_clusters}
                        max={GRAPH.job_param_clusters_max}
                        marks={marks_clusters}
                        onAfterChange={this.updateClusters}/>
                      <br/>
                  </div> : null}
                  {state.clusterToNodes ? <div className='list-group'>
                        {Object.keys(state.clusterToNodes).map(key => {
                          var meta = state.nodes_meta['c-' + key];
                          return <ClusterNodes
                            i={key}
                            key={key}
                            size={state.clusterToNodes[key].length}
                            label={meta && meta['label'] ? meta['label'] : undefined}
                            update_label={state.update_cluster_label}
                            />;
                      })}
                  </div> : null}
              </div>
            </div> : null}
            {this.state.tab == 'advanced' ?
            <div>
              <div className='panel panel-primary'>
                  <div className='panel-heading'>
                      <h3 className='panel-title'>{GRAPH.name}</h3>
                  </div>
                  {!GRAPH.magic_too_big_to_display_X ? <div className='panel-body'>
                      <strong>{state.n_edges}</strong> edges, <strong>{state.n_nodes}</strong> nodes
                      <br/>
                      imported <strong>{GRAPH.created_at}</strong><br/>
                      time taken <strong>{GRAPH.time}</strong><br/>
                      {GRAPH.result && false ? 
                        <span>
                          clustering score: <strong>{GRAPH.result.crit}</strong>
                        </span>
                        : null}
                  </div> : null}
              </div>
              {GRAPH.USE_EXPERIMENTAL_WEBGL_MODE  ? <p>
                <button href="#" className="btn btn-primary btn-xs" onClick={() => {
                  GRAPH.USE_EXPERIMENTAL_WEBGL_MODE = false;
                  init();
                }}>go back to SVG mode</button>
              </p> : <p>
                <button href="#" className="btn btn-primary btn-xs" onClick={() => {
                  GRAPH.USE_EXPERIMENTAL_WEBGL_MODE = true;
                  init();
                }}>use WebGL (experimental)</button>
              </p>}
              <div className='panel panel-default'>
                  <div className='panel-heading'>
                      <h3 className='panel-title'>
                        <abbr title='minimum connectivity (PI) between clusters to show a link between them (helpful when you have many clusters)'>
                          cluster-to-cluster cutoff
                        </abbr> - {(this.state.cutoff).toExponential(4)} %</h3>
                  </div>
                  <div className='panel-body'>
                      <Slider step={0.001} defaultValue={this.state.cutoff}
                        min={0}
                        max={2}
                        handle={handle}
                        onAfterChange={this.updateCutoff}/>
                      <br/>
                  </div>
              </div>
              {GRAPH.scores && GRAPH.scores.length > 0 ? <div className='panel panel-default'>
                  <div className='panel-heading'>
                      <h3 className='panel-title'>Clusterings ordered by score</h3>
                  </div>
                  <div className='panel-body'>
                    <table className='table table-striped table-bordered'>
                      <thead>
                        <tr>
                          <th>Clusters</th>
                          <th>Topics</th>
                          <th>Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {GRAPH.scores.map((v,i) => <tr
                            className={this.state.clusters == v[0] && this.state.topics == v[1] ? 'info' : ''}>
                          <td>{v[0]}</td>
                          <td>{v[1]}</td>
                          <td>{v[2]  ? v[2].toFixed(2) : 'clustering failed'}</td>
                        </tr>)}
                      </tbody>
                    </table>
                  </div>
              </div> : null}
            </div> : null}
            {this.state.tab == 'log' ? <pre>{GRAPH.log}</pre> : null}
        </div>;
    }
}

export default state => {
    ReactDOM.render(<Sidebar state={state} />, document.getElementById('_sidebar'));
};
