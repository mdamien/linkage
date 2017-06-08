import React from 'react';
import ReactDOM from 'react-dom';

function render(curr_tab, changeTab) {
  var tabs = [{
    title: 'Graph',
    id: 'graph',
  }];
  
  if (!GRAPH.magic_too_big_to_display_X) {
    tabs.push({
      title: 'Adjacency Matrix',
      id: 'matrix',
    });
  }

  tabs.push({
    title: 'Statistics',
    id: 'viz',
  });

  /*
  tabs.push({
    title: 'Graph',
    id: 'graph2',
  });
  */

  var buttons = <ul className="nav nav-tabs">
      {tabs.map((tab, i) => <li key={i} className={tab.id == curr_tab ? 'active' : ''}>
        <a href='#'
          onClick={() => changeTab(tab.id)}>
            {tab.title}
        </a>
      </li>)}
    </ul>;

  ReactDOM.render(buttons, document.getElementById('_graph-tabs'));
};

export default render;
