import { get_color } from './utils';

function render(state) {

  var bars = []

  Object.keys(state.clusterToNodes).map(key => {
    var key = parseInt(key); // TODO: fix key being a string and remove those parseInt
    var meta = state.nodes_meta['c-' + key];
    var label = meta && meta['label'] ? meta['label'] : ('cluster ' + key);
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
    animations: [],
    showlegend: false,
  };

  Plotly.newPlot(document.getElementById('tester'), bars, layout);
};

export default render;
