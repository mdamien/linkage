import React from 'react';
import ReactDOM from 'react-dom';

function render(curr_tab, changeTab) {
  var tabs = [
    {
      title:'Graph',
      id: 'graph',
    },/*
    {
      title: 'Adjacency Matrix',
      id: 'matrix',
    },*/
    {
      title: 'Clustering infos',
      id: 'viz',
    },
  ];

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
