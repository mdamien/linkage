import React from 'react';
import ReactDOM from 'react-dom';

import { hashedColor } from './utils';

var ColorSquare = color => <span className='label' style={{ backgroundColor: color, marginRight: 10 }}> </span>;

export default state => {
    var sidebar = <div>
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
            <div className='list-group'>
                {Object.keys(state.clusterToNodes).map(key => 
                    <div className='list-group-item' key={key}>
                        {ColorSquare(hashedColor(key))} {key} ({state.clusterToNodes[key].length})
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
                                <span className="label label-default" key={i}>{t}</span>&nbsp;
                            </span> : null
                        )}
                    </div>
                )}
            </div>
        </div> : null}
    </div>;

    ReactDOM.render(sidebar, document.getElementById('_sidebar'));
};