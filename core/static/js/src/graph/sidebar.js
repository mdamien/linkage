import React from 'react';
import ReactDOM from 'react-dom';
import Slider from 'rc-slider';

import { hashedColor } from './utils';

var ColorSquare = color => <span className='label' style={{ backgroundColor: color, marginRight: 10 }}> </span>;

class Sidebar extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        showLog: false,
        clusters: 4,
        topics: 3,
      };
      this.toggleLog = this.toggleLog.bind(this);
      this.updateClusters = this.updateClusters.bind(this);
    }
    toggleLog() {
        this.setState({showLog: !this.state.showLog});
    }
    updateClusters(clusters) {
        this.setState({clusters: clusters});
        $.post('/result/' + GRAPH.id + '/cluster_it/', {
            clusters: this.state.clusters,
            topics: this.state.topics,
        }, function(data) {
            console.log(data);
        });
    }
    render() {
        var state = this.props.state;
        return <div>
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
            {state.clusterToNodes ? <div className='panel panel-default'>
                <div className='panel-heading'>
                    <h3 className='panel-title'>Clusters - {Object.keys(state.clusterToNodes).length}</h3>
                </div>
                <div className='panel-body'>
                    <Slider steps={1} dots defaultValue={this.state.clusters} min={2} max={10} marks={{
                        2: '2',
                        10: '10',
                    }} onAfterChange={this.updateClusters}/>
                    <br/>
                </div>
                <div className='list-group'>
                    {Object.keys(state.clusterToNodes).map(key => 
                        <div className='list-group-item' key={key}>
                            {ColorSquare(hashedColor(key))} {state.clusterToNodes[key].length}
                        </div>
                    )}
                </div>
            </div> : <div className='alert alert-info'>
                processing graph...
                <div className="progress progress-striped active hide">
                  <div className="progress-bar progress-bar-success" style={{width: '10%'}}></div>
                </div>
            </div>}
            {state.topicToEdgesPercentage ? <div className='panel panel-default'>
                <div className='panel-heading'>
                    <h3 className='panel-title'>Topics - {state.topicToEdgesPercentage.length}</h3>
                </div>
                <div className='list-group'>
                    {state.topicToEdgesPercentage.map((v, i) => 
                        <div className='list-group-item' key={i}>
                            {ColorSquare(hashedColor(''+i))} {i} ({v.toFixed(2) + ' %'})
                            <br/>ex: {state.topicToTerms[i].slice(0, 10).map((t, i) =>
                                i % 2 == 0 ? <span key={i}>
                                    <span
                                        className="label label-default"
                                        key={i}
                                    >{t}</span>{' '}
                                </span> : null
                            )}
                        </div>
                    )}
                </div>
            </div> : null}
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