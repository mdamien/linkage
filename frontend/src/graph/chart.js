import { get_color } from './utils';

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
    title: 'Clusters node count',
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


  var z = STATE.labels.map((_, source) => {
    return STATE.labels.map((_, target) => {
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
        return topic_max;
      }
      return null;
    });
  });

  const n_topics = STATE.topicToTerms.length;
  var colorscale = STATE.topicToTerms.map((_, i) => {
    return [i/(n_topics-1), get_color(i)];
  });

  var data = [
    {
      z,
      x: STATE.labels,
      y: STATE.labels,
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
  };

  Plotly.newPlot('_matrix-viz', data, layout);
  $('#_matrix-viz-wrapper').show();
};

function render(state) {
  renderBarPlot(state);
  if (!GRAPH.magic_too_big_to_display_X) renderMatrix(state);
};

export default render;
