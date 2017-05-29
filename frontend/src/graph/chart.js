import React from 'react';
import ReactDOM from 'react-dom';

import { get_color, n_best_elems } from './utils';

var ColorSquare = (color, content=' ')  => <span className='label' style={{ backgroundColor: color, marginRight: 10 }}>{content}</span>;

function renderBarPlot(state) {
  var bars = []

  Object.keys(state.clusterToNodes).map(key => {
    var key = parseInt(key); // TODO: fix key being a string and remove those parseInt
    var meta = state.nodes_meta['c-' + key];
    var label = meta && meta['label'] ? ('cluster ' + key + ' - ' + meta['label']) : ('cluster ' + key);
    bars.push({
      x: [label],
      y: [state.clusterToNodes[key].length],
      type: 'bar',
      marker: {
        color: get_color(key, 'Paired'),
      }
    })
  });

  var layout = {
    title: 'Nodes per cluster',
    showlegend: false,
  };

  Plotly.newPlot('_bar-plot', bars, layout);
};

function renderMatrix(STATE) {
  /*
    ..... nodes.....
    .
    .       [x] <- topic of the link
    .
    . 
    . <-- nodes

  */

  var sorted_labels = n_best_elems(STATE.labels, undefined, (v, i) => {
    return STATE.nodeToCluster[i];
  });

  var z = sorted_labels.map(source_it => {
    var source = source_it[0];
    return sorted_labels.map(target_it => {
      var target = target_it[0];
      var link_id = STATE.edges.indexOf(source + ',' + target);
      if (link_id === -1 && !GRAPH.directed) {
        link_id = STATE.edges.indexOf(target + ',' + source);
      }
      if (STATE.topics_per_edges && link_id !== -1) {
        var topic_max = -1;
        var topic_max_value = null;
        STATE.topics_per_edges.forEach((row, topic) => {
          var v = row[link_id];
          if (topic_max_value === null || v > topic_max_value) {
            topic_max_value = v;
            topic_max = topic;
          }
        });
        return topic_max + 1;
      }
      return 0;
    });
  });

  const n_topics = STATE.topicToTerms.length;
  var colorscale = [[0, '#eee']];
  STATE.topicToTerms.forEach((_, i) => {
    colorscale.push([(i+1)/(n_topics), get_color(i)]);
  });

  var colored_labels = sorted_labels.map(it => {
    var i = it[0];
    var label = it[1];
    var cluster = STATE.nodeToCluster[i];
    var color = get_color(cluster, 'Paired');
    return '<span style="color:' + color + '" onClick="alert(42)">' + label + '</span>';
  });

  var data = [
    {
      z,
      x: colored_labels,
      y: colored_labels,
      type: 'heatmap',
      colorscale,
      showscale: false,
      xgap: 5,
      ygap: 5,
    }
  ];

  var layout = {
    title: 'Topics per edges',
    showlegend: false,
    xaxis: {
      type: 'category',
      tickangle: 45,
    },
    yaxis: {
      type: 'category',
      tickangle: 45,
    }
  };

  Plotly.newPlot('_matrix-viz', data, layout);
  $('#_matrix-viz-wrapper').show();
};

function renderWordPlot(state) {
  var COL_WIDTH = (1 / state.topicToTerms.length * 100).toFixed(2) + '%';
  ReactDOM.render(<div>
    <h4 className='text-center'>Topics top words</h4>
    <br/>
    <div className='row'>
          {state.topicToTermsTFIDF.map((words, i) => {
            var best = n_best_elems(words, 10, word => word.tfidf);
            var label = state.dictionnary[best[0][0]];
            var topic_meta = state.nodes_meta['t-' + i];
            if (topic_meta && topic_meta['label']) {
              label = topic_meta['label'];
            }
            return <div className={'col-md-3'} style={{width: COL_WIDTH}} key={i}>
              <h5 className='text-center'>{ColorSquare(get_color(i), label)}</h5>
              <ul>{best.map((t, i) => {
                return <li key={i}>{state.dictionnary[t[0]]}</li>;
              })}
              </ul>
            </div>
          })}
      </div>
    </div>, document.getElementById('_words-plot'));
};

function render(state) {
  renderBarPlot(state);
  renderWordPlot(state);
  if (!GRAPH.magic_too_big_to_display_X) renderMatrix(state);
};

export default render;
