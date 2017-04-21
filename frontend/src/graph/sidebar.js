import React from 'react';
import ReactDOM from 'react-dom';
import Slider from 'rc-slider';
import Tooltip from 'rc-tooltip';

// import { styles } from 'react-autocomplete/lib/utils'
// import Autocomplete from 'react-autocomplete'

import { get_color, hashedColor, n_best_elems } from './utils';
import { init, display_loading } from '../graph';

var ColorSquare = (color, content=' ')  => <span className='label' style={{ backgroundColor: color, marginRight: 10 }}>{content}</span>;


export function sortStates (a, b, value) {
  return (
    a.toLowerCase().indexOf(value.toLowerCase()) >
    b.toLowerCase().indexOf(value.toLowerCase()) ? 1 : -1
  )
}
/*
let App = React.createClass({
  getInitialState() {
    return { value: '' }
  },
  render () {
    return (
      <div className='panel panel-default panel-body'>
        <label htmlFor="states-autocomplete">Search</label>{' '}
        <Autocomplete
          value={this.state.value}
          inputProps={{name: "US state", id: "states-autocomplete"}}
          items={this.props.choices}
          getItemValue={(item) => item}
          shouldItemRender={(item, value) => 
            item.toLowerCase().indexOf(value.toLowerCase()) !== -1
          }
          onChange={(event, value) => this.setState({ value })}
          onSelect={value => this.setState({ value })}
          renderItem={(item, isHighlighted) => (
            <div
              style={isHighlighted ? styles.highlightedItem : styles.item}
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
*/

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
        let {i, words, dictionnary} = this.props;
        return <div className='list-group-item'>
            {ColorSquare(get_color(i))}
            ex: {n_best_elems(words, 5, v => v.tfidf).map((t, i) => {
                return <span key={i}>
                    <span
                        className="label label-default"
                        key={i}
                    >{dictionnary[t[0]]}</span>{' '}
                </span>
            })}
            <p style={{marginTop: 10}}>
                <a className='btn btn-warning btn-xs' onClick={this.toggleShow}>
                    {this.state.showAll ? 'hide' : 'show'} details
                </a>
            </p>
            {this.state.showAll ? <table className='table table-striped table-bordered'>
                <tbody>
                    {n_best_elems(words, 1000, v => v.tfidf).map((t, i) => {
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
        showLog: false,
        clusters: GRAPH.result ? GRAPH.result.param_clusters : 3,
        topics: GRAPH.result ? GRAPH.result.param_topics : 3,
        cutoff: GRAPH.cluster_to_cluster_cutoff,
      };
      this.toggleLog = this.toggleLog.bind(this);
      this.updateClusters = this.updateClusters.bind(this);
      this.updateTopics = this.updateTopics.bind(this);
      this.updateCutoff = this.updateCutoff.bind(this);

      if (GRAPH.result) {
        this.props.state.current_selected_topics = this.state.topics;
        this.props.state.current_selected_clusters = this.state.clusters;
      }
    }
    toggleLog() {
        this.setState({showLog: !this.state.showLog});
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
        GRAPH.cluster_to_cluster_cutoff = cutoff;
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
            {/*<App choices={state.labels} />*/}
            <div className='panel panel-primary'>
                <div className='panel-heading'>
                    <h3 className='panel-title'>{GRAPH.name}</h3>
                </div>
                <div className='panel-body'>
                    <strong>{state.n_edges}</strong> edges, <strong>{state.n_nodes}</strong> nodes
                    <br/>
                    imported <strong>{GRAPH.created_at}</strong><br/>
                    {GRAPH.result && false ? 
                      <span>
                        clustering score: <strong>{GRAPH.result.crit}</strong>
                      </span>
                      : null}
                </div>
            </div>
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
                        <TopicWords words={v} i={i} key={i} dictionnary={state.dictionnary}/>
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
                    <div className='list-group-item'>
                      {Object.keys(state.clusterToNodes).map(key => 
                          <span key={key}>
                            {ColorSquare(get_color(key, 'Paired'), state.clusterToNodes[key].length)}{' '}
                          </span>
                      )}
                    </div>
                </div> : null}
            </div>
            <div className='panel panel-default'>
                <div className='panel-heading'>
                    <h3 className='panel-title'>Result</h3>
                </div>
                {GRAPH.result ? <div className='panel-body'>
                    time taken <strong>{(GRAPH.time*100).toFixed(2)}s</strong><br/>
                    clustering score: <strong>{GRAPH.result.crit}</strong><br/>
                    {GRAPH.log ? <div>
                        <a className='btn btn-info btn-xs' onClick={this.toggleLog}>
                            {this.state.showLog ? 'hide' : 'show'} log
                        </a>
                        {this.state.showLog ? <div>
                            <br/>
                            <pre>{GRAPH.log}</pre>
                        </div> : null}
                    </div> : null}
                </div> : <div className='panel-body'>
                    {GRAPH.result && GRAPH.progress == 1 ?
                        'An error occured while processing.'
                        : 'Processing graph...'}
                </div>}
            </div>
            <div className='panel panel-default'>
                <div className='panel-heading'>
                    <h3 className='panel-title'>cluster-to-cluster cutoff - {this.state.cutoff}</h3>
                </div>
                <div className='panel-body'>
                    <Slider step={0.00001} defaultValue={this.state.cutoff}
                      min={0}
                      max={0.005}
                      handle={handle}
                      onAfterChange={this.updateCutoff}/>
                    <br/>
                </div>
            </div>
        </div>;
    }
}

export default state => {
    ReactDOM.render(<Sidebar state={state} />, document.getElementById('_sidebar'));
};
