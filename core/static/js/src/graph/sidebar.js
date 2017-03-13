import React from 'react';
import ReactDOM from 'react-dom';
import Slider from 'rc-slider';

import { styles } from 'react-autocomplete/lib/utils'
import Autocomplete from 'react-autocomplete'

import { hashedColor, n_best_elems } from './utils';

var ColorSquare = color => <span className='label' style={{ backgroundColor: color, marginRight: 10 }}> </span>;


export function sortStates (a, b, value) {
  return (
    a.toLowerCase().indexOf(value.toLowerCase()) >
    b.toLowerCase().indexOf(value.toLowerCase()) ? 1 : -1
  )
}

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
            {ColorSquare(hashedColor('t'+i))}
            ex: {n_best_elems(words, 5).map((t, i) => {
                if (t[1] < 0.001) return null;
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
                    {n_best_elems(words).map((t, i) => {
                        if (t[1] < 0.001) return null;
                        return <tr key={i}>
                            <td>{dictionnary[t[0]]}</td>
                            <td className='text-right'>{(t[1] * 100).toFixed(2)} %</td>
                        </tr>;
                    })}
                </tbody>
            </table> : null}
        </div>
    }
};

class Sidebar extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        showLog: false,
        clusters: GRAPH.result.param_clusters,
        topics: GRAPH.result.param_topics,
      };
      this.toggleLog = this.toggleLog.bind(this);
      this.updateClusters = this.updateClusters.bind(this);
      this.updateTopics = this.updateTopics.bind(this);
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
        });
    }
    updateTopics(topics) {
        this.setState({topics: topics});
        $.post('/result/' + GRAPH.id + '/cluster_it/', {
            clusters: this.state.clusters,
            topics: topics,
        }, function(data) {
            console.log(data);
        });
    }
    render() {
        var state = this.props.state;
        return <div>
            <App choices={state.labels} />
            <div className='panel panel-primary'>
                <div className='panel-heading'>
                    <h3 className='panel-title'>{GRAPH.name}</h3>
                </div>
                <div className='panel-body'>
                    <strong>{state.n_edges}</strong> edges
                    <br/>
                    <strong>{state.n_nodes}</strong> nodes
                    <br/>
                    imported <strong>{GRAPH.created_at}</strong>
                </div>
            </div>
            <div className='panel panel-default'>
                <div className='panel-heading'>
                    <h3 className='panel-title'>Clusters 
                        {state.clusterToNodes ?
                            <span> - {Object.keys(state.clusterToNodes).length}</span>
                            : null}
                    </h3>
                </div>
                <div className='panel-body'>
                    <Slider steps={1} dots defaultValue={this.state.clusters} min={2} max={10} marks={{
                        2: '2',
                        10: '10',
                    }} onAfterChange={this.updateClusters}/>
                    <br/>
                </div>
                {state.clusterToNodes ? <div className='list-group'>
                    {Object.keys(state.clusterToNodes).map(key => 
                        <div className='list-group-item' key={key}>
                            {ColorSquare(hashedColor(key))} {state.clusterToNodes[key].length}
                        </div>
                    )}
                </div> : <div className='list-group-item'>
                    {GRAPH.result && GRAPH.result.progress == 1 ?
                        'An error occured while processing.'
                        : 'Processing graph...'}
                </div>}
            </div>
            <div className='panel panel-default'>
                <div className='panel-heading'>
                    <h3 className='panel-title'>Topics 
                        {state.topicToTerms ?
                            <span> - {state.topicToTerms.length}</span>
                            : null}
                    </h3>
                </div>
                <div className='panel-body'>
                    <Slider steps={1} dots defaultValue={this.state.topics} min={2} max={10} marks={{
                        2: '2',
                        10: '10',
                    }} onAfterChange={this.updateTopics}/>
                    <br/>
                </div>
                {state.topicToTerms ? <div className='list-group'>
                    {state.topicToTerms.map((v, i) => 
                        <TopicWords words={v} i={i} key={i} dictionnary={state.dictionnary}/>
                    )}
                </div> : null}
            </div>
            {GRAPH.result && GRAPH.result.log ? <div>
                <a className='btn btn-info btn-xs' onClick={this.toggleLog}>
                    {this.state.showLog ? 'hide' : 'show'} log
                </a>
                {this.state.showLog ? <div>
                    <br/>
                    <pre>{GRAPH.result.log}</pre>
                </div> : null}
            </div> : null}
        </div>;
    }
}

export default state => {
    ReactDOM.render(<Sidebar state={state} />, document.getElementById('_sidebar'));
};