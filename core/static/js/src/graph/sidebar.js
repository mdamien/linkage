import React from 'react';
import ReactDOM from 'react-dom';

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
                        {key} ({state.clusterToNodes[key].length})
                    </div>
                )}
            </div>
        </div> : <div className='alert alert-info'>processing graph...</div>}
        {state.topicToEdgesPercentage ? <div className='panel panel-default'>
            <div className='panel-heading'>
                <h3 className='panel-title'>Topics - {state.topicToEdgesPercentage.length}</h3>
            </div>
            <div className='list-group'>
                {state.topicToEdgesPercentage.map((v, i) => 
                    <div className='list-group-item' key={i}>
                        {i} ({v.toFixed(2) + ' %'})
                    </div>
                )}
            </div>
        </div> : null}
    </div>;

    ReactDOM.render(sidebar, document.getElementById('_sidebar'));
};