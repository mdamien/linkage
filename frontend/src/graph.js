import './graph/csrf.js';

import renderSidebar from './graph/sidebar';
import renderGraphSidebar from './graph/info';
import renderGraphButtons from './graph/graph_buttons';

import { get_color, hashedColor, COLORS, edgesArr, n_best_elems } from './graph/utils';
import tfidf from './graph/tf_idf';

// TODO: STATE is here to keep computed things in memory, could be cleaned up
var STATE = null;
var RENDERER = null;

function init(state_init = {}) {
  STATE = state_init;
  var graph = Viva.Graph.graph();

  var labels = Papa.parse(GRAPH.labels, {delimiter: ' ', skipEmptyLines: true}).data[0];
  var X = Papa.parse(GRAPH.edges, {delimiter: ' ', dynamicTyping: true, skipEmptyLines: true}).data;
  var tdm = Papa.parse(GRAPH.tdm, {delimiter: ' ', skipEmptyLines: true}).data;
  var dictionnary = Papa.parse(GRAPH.dictionnary, {delimiter: ' ', skipEmptyLines: true}).data[0];

  // remove extra empty edge
  if (X.length > 0 && X[X.length-1][2] == 0) {
    X = X.slice(0, X.length - 1);
  }

  if (!labels || !X) {
    $('#_loading').text('No data for this graph');
    return;
  }

  STATE.labels = labels;
  STATE.n_edges = X.length;
  STATE.n_nodes = labels.length;
  STATE.dictionnary = dictionnary;
  STATE.edges = edgesArr(X);
  STATE.tdm = tdm;

  if (GRAPH.result && GRAPH.result.clusters_mat) {
    var nodeToCluster = parse_txt_mat(GRAPH.result.clusters_mat)[0];

    var clusterToNodes = {};
    nodeToCluster.forEach(function(cluster, node) {
      if (!(cluster in clusterToNodes)) {
        clusterToNodes[cluster] = []
      }
      clusterToNodes[cluster].push(node);      
    });
    STATE.clusterToNodes = clusterToNodes;

    var topics = parse_txt_mat(GRAPH.result.topics_mat);

    STATE.topicToTerms = topics;

    STATE.topicToTermsTFIDF = tfidf(topics);

    STATE.topicsName = STATE.topicToTermsTFIDF.map(words =>
      dictionnary[n_best_elems(words, 1, v => v.tfidf)[0][0]]
    );

    var topics_per_edges = parse_txt_mat(GRAPH.result.topics_per_edges_mat);

    STATE.topics_per_edges = topics_per_edges;

    STATE.rho = Papa.parse(GRAPH.result.rho_mat,
      {delimiter: ',', dynamicTyping: true, skipEmptyLines: true}).data;

    STATE.theta_qr = parse_txt_mat(GRAPH.result.theta_qr_mat);

    STATE.pi = parse_txt_mat(GRAPH.result.pi_mat);

    STATE.nodes_meta = GRAPH.result.nodes_meta ? JSON.parse(GRAPH.result.nodes_meta) : {};

    _add_clusters(graph, X, nodeToCluster);
  } else {
    X.forEach(function(line, i) {
      graph.addLink(line[0], line[1], {link_id: i});
    });
  }

  document.getElementById('_graph').innerHTML = '';

  var layout = Viva.Graph.Layout.forceDirected(graph, {
    springLength: 80,
    springCoeff: 0.0002,
  });

  RENDERER = Viva.Graph.View.renderer(graph, {
    layout: layout,
    container: document.getElementById('_graph'),
    graphics: get_graph_graphics(graph, X, nodeToCluster),
  });

  $('#_loading').hide();

  var timeout = false;
  STATE.graph_layout_running = false;
  RENDERER.pause_in = (time) => {
    if (timeout) {
      clearTimeout(timeout);
    }
    if (time != 0 && !STATE.graph_layout_running) {
      RENDERER.resume();
      STATE.graph_layout_running = true;
    }
    renderGraphButtons({
      renderer: RENDERER,
      expand_clusters: expand_clusters.bind(this, graph, X, nodeToCluster),
      collapse_clusters: collapse_clusters.bind(this, graph, X, nodeToCluster),   
      graph_layout_running: STATE.graph_layout_running,
      fit_graph: fit_graph,
    });
    timeout = setTimeout(function() {
      RENDERER.pause();
      STATE.graph_layout_running = false;
      renderGraphButtons({
        renderer: RENDERER,
        expand_clusters: expand_clusters.bind(this, graph, X, nodeToCluster),
        collapse_clusters: collapse_clusters.bind(this, graph, X, nodeToCluster),   
        graph_layout_running: STATE.graph_layout_running,
        fit_graph: fit_graph,
      });
    }, time);
  };

  RENDERER.clear_pause_in = () => {
    if (timeout) {
      clearTimeout(timeout);
    }
    if (!STATE.graph_layout_running) {
      RENDERER.resume();
      STATE.graph_layout_running = true;
    }
    renderGraphButtons({
      renderer: RENDERER,
      expand_clusters: expand_clusters.bind(this, graph, X, nodeToCluster),
      collapse_clusters: collapse_clusters.bind(this, graph, X, nodeToCluster),   
      graph_layout_running: STATE.graph_layout_running,
      fit_graph: fit_graph,
    });
  }

  STATE.graph_layout_running = true;
  RENDERER.run();
  RENDERER.pause_in(2000);

  RENDERER.layout = layout;
  RENDERER.graph = graph;

  renderSidebar(STATE);
  renderGraphSidebar({
    renderer: RENDERER,
    expand_clusters: expand_clusters.bind(this, graph, X, nodeToCluster),
    collapse_clusters: collapse_clusters.bind(this, graph, X, nodeToCluster),
  });
  renderGraphButtons({
    renderer: RENDERER,
    expand_clusters: expand_clusters.bind(this, graph, X, nodeToCluster),
    collapse_clusters: collapse_clusters.bind(this, graph, X, nodeToCluster),   
    graph_layout_running: STATE.graph_layout_running,
    fit_graph: fit_graph,
  });

  update_graph_height();
}

function parse_txt_mat(mat) {
  return mat.split('\n').map(line =>
    line.split(' ').filter(x => x).map(x => parseFloat(x))
  ).filter(line => line.length > 0);
}

function fit_graph() {
  // https://github.com/anvaka/VivaGraphJS/blob/a5c5c92cdecd6964b0bb0c1cb0aaa63c30ffc9e4/demos/other/precompute-advanced.html#L62-L77
  var graphRect = RENDERER.layout.getGraphRect();
  var graphSize = Math.min(graphRect.x2 - graphRect.x1, graphRect.y2 - graphRect.y1);
  var g = $('#_graph svg')[0];
  var screenSize = Math.min(g.clientWidth, g.clientHeight);
  var desiredScale = screenSize / graphSize;
  RENDERER.moveTo((graphRect.x2 + graphRect.x1)/2, (graphRect.y2 + graphRect.y1)/2);
  RENDERER.scale(desiredScale);
}

function zoom_on(node_id) {
  if (RENDERER.graph.getNode(node_id)) {
    var pos = RENDERER.layout.getNodePosition(node_id);
    RENDERER.moveTo(pos.x, pos.y);
  } else {
    alert('The selected node is not visible');
  }
}

function update_cluster_label(cluster, label) {
  if (label === '') {
    label = cluster;
  }
  STATE.nodes_meta['c-' + cluster] = {
    label
  };
  GRAPH.result.nodes_meta = JSON.stringify(STATE.nodes_meta);
  renderSidebar(STATE);
  RENDERER.rerender();
  $.post('/result/' + GRAPH.id + '/update_clusters_labels/', {
      clusters: GRAPH.result.param_clusters,
      topics: GRAPH.result.param_topics,
      nodes_meta: JSON.stringify(STATE.nodes_meta),
  });
}

function expand_cluster(cluster_name, graph, X, clusters) {
  // remove current node
  graph.removeNode('c-' + cluster_name);

  // add all nodes of the cluster
  X.forEach(function(line, i) {
    // if origin node in cluster, add it
    if (clusters[line[0]] == cluster_name) {
      if (graph.getNode(line[1]) || clusters[line[1]] == cluster_name) {
        graph.addLink(line[0], line[1], {link_id: i});
      } else {
        // if target node not yet expanded, link to the cluster
        graph.addLink(line[0], 'c-' + clusters[line[1]]);
      }
    }
    // if target node in cluster, add it
    else if (clusters[line[1]] == cluster_name) {
      if (graph.getNode(line[0]) || clusters[line[0]] == cluster_name) {
        graph.addLink(line[0], line[1], {link_id: i});
      } else {
        // if origin node not yet expanded, link to the cluster
        graph.addLink('c-' + clusters[line[0]], line[1]);
      }
    }
  });
}

function expand_clusters(graph, X, clusters) {
  graph.clear()

  X.forEach(function(line, i) {
    graph.addLink(line[0], line[1], {link_id: i});
  });

  RENDERER.pause_in(2000);
}

function _add_clusters(graph, X, nodeToCluster) {
  var added_links = new Set();

  var clusters = new Set();
  nodeToCluster.forEach(x => clusters.add(x));

  clusters.forEach(function(cluster0) {
    clusters.forEach(function(cluster1) {
      var key = cluster0 + ',' + cluster1;
      if (added_links.has(key)) return;
      added_links.add(key);
      if (cluster0 === undefined) {
        console.log('invalid cluster0', cluster0, 'for', line);
        return;
      }
      if (cluster1 === undefined) {
        console.log('invalid cluster1', cluster1, 'for', line);
        return;
      }
      graph.addNode('c-' + cluster0, {isCluster: true});
      graph.addNode('c-' + cluster1, {isCluster: true});
      if (STATE.pi[cluster0][cluster1] > GRAPH.cluster_to_cluster_cutoff) {
        graph.addLink('c-' + cluster0, 'c-' + cluster1);
      }
    })
  });
}

function collapse_clusters(graph, X, clusters) {
  graph.forEachNode(function(node){
    graph.removeNode(node.id);
  });

  _add_clusters(graph, X, clusters);

  RENDERER.pause_in(2000);
}

function save_clusters_pos(graph) {
  var positions = {};
  graph.forEachNode(node => {
    if (node.data && node.data.isCluster) {
      var pos = RENDERER.layout.getNodePosition(node.id);
      positions[node.id] = {
        x: pos.x,
        y: pos.y,
      };
    }
  });
  console.log('sending', JSON.stringify(positions, null, 2));
}

function get_graph_graphics(graph, X, clusters) {
    var last_mouse_down_event = null;

    var graphics = Viva.Graph.View.svgGraphics(),
        nodeSize = 20;

    graphics.node(function(node) {
      var is_cluster = node.data && node.data.isCluster;
      var cluster_name = is_cluster ? parseInt(node.id.split('-')[1]) : null;
      var cluster_label = null;
      if (STATE.nodes_meta[node.id] && STATE.nodes_meta[node.id]['label']) {
        cluster_label = STATE.nodes_meta[node.id]['label'];
      } else {
        cluster_label = '' + cluster_name;
      }

      var color = '#aaa';

      if (is_cluster) {
        color = get_color(cluster_name, 'Paired');
      }

      if (!is_cluster && clusters && clusters[node.id] !== undefined) {
        color = get_color(clusters[node.id], 'Paired');
      }
      var ui = Viva.Graph.svg('g'),
          circle = Viva.Graph.svg('circle')
            .attr('cx', 0)
            .attr('cy', 0)
            .attr('stroke', 'black')
            .attr('stroke-width', '0')
            .attr('style', 'fill: ' + color)
            .attr('r', 7),
          square = Viva.Graph.svg('rect')
            .attr('stroke', 'black')
            .attr('stroke-width', '0')
            .attr('style', 'fill: ' + color);
      if (is_cluster) {
        var sorted = n_best_elems(STATE.rho, false, v => v[0]);
        var max = sorted[0][1][0];
        var min = sorted.slice(-1)[0][1][0];
        var normalized = (STATE.rho[cluster_name][0] - min) / (max - min);
        if (!normalized) {
          normalized = 0;
        }
        var size = 20 + Math.exp(normalized * 3);
        square.attr('x', -size/2);
        square.attr('y', -size/2);
        square.attr('width', size);
        square.attr('height', size);
        node._node_size = size;
        ui.append(square);
      } else {
        node._node_size = 7*2;
        ui.append(circle);
      }

      if (is_cluster) {
        var svgText = Viva.Graph.svg('text')
          .attr('y', '5px')
          .attr('x', (node._node_size / 2 + 5) + 'px');
        ui.append(svgText);
        ui._node_id = node.id;
        ui._text = svgText; 
      }
      ui._is_cluster = is_cluster;

      // svgText.attr('visibility', 'hidden');
      $(ui).hover(function() {
        // svgText.attr('visibility', 'visible');
        circle.attr('stroke-width', '1');
        square.attr('stroke-width', '1');

        var top_nodes = [];
        if (is_cluster) {
          if (GRAPH.result && GRAPH.result.top_nodes) {
            top_nodes = GRAPH.result.top_nodes[cluster_name];
          } else {
            top_nodes = STATE.clusterToNodes[cluster_name].slice(0, 5).map(x => STATE.labels[x])
            .filter(x => x);
          }
        }

        renderGraphSidebar({
          title: node.data && node.data.isCluster ? cluster_name : STATE.labels[node.id],
          cluster_label: cluster_label,
          update_cluster_label: update_cluster_label,
          is_node: true,
          is_cluster: is_cluster,
          cluster: is_cluster || !clusters ? undefined : clusters[node.id],
          renderer: RENDERER,
          top_nodes,
          expand_clusters: expand_clusters.bind(this, graph, X, clusters),
          collapse_clusters: collapse_clusters.bind(this, graph, X, clusters),
        });
        renderGraphButtons({
          renderer: RENDERER,
          expand_clusters: expand_clusters.bind(this, graph, X, clusters),
          collapse_clusters: collapse_clusters.bind(this, graph, X, clusters),
          graph_layout_running: STATE.graph_layout_running, 
          fit_graph: fit_graph,
        });
      }, function() {
        circle.attr('stroke-width', '0');
        square.attr('stroke-width', '0');
        // svgText.attr('visibility', 'hidden');
      });

      $(ui).mousedown(event => {
        last_mouse_down_event = event;
      });

      $(ui).click(function(event) {
        console.log('clicked on', node);
        if (event.offsetX != last_mouse_down_event.offsetX ||
          event.offsetY != last_mouse_down_event.offsetY) {
          save_clusters_pos(graph);
          return;
        }
        if (is_cluster) {
          expand_cluster(cluster_name, graph, X, clusters);

          RENDERER.pause_in(2000);
        }
      });

      return ui;
    }).placeNode(function(nodeUI, pos) {
      if (nodeUI._is_cluster) {
        var meta = STATE.nodes_meta[nodeUI._node_id];
        var label = '';
        if (meta && meta['label']) {
          label = meta['label'];
        }
        nodeUI._text.text(label);
      }
      nodeUI.attr('transform',
                  'translate(' +
                        (pos.x) + ',' + (pos.y) +
                  ')');
    });

    // To render an arrow we have to address two problems:
    //  1. Links should start/stop at node's bounding box, not at the node center.
    //  2. Render an arrow shape at the end of the link.
    // Rendering arrow shape is achieved by using SVG markers, part of the SVG
    // standard: http://www.w3.org/TR/SVG/painting.html#Markers
    var createMarker = function(id) {
            return Viva.Graph.svg('marker')
                       .attr('id', id)
                       .attr('viewBox', "0 0 10 10")
                       .attr('refX', "10")
                       .attr('refY', "5")
                       .attr('markerUnits', "userSpaceOnUse")
                       .attr('markerWidth', "5")
                       .attr('markerHeight', "2.5")
                       .attr('orient', "auto");
        },
        marker = createMarker('Triangle');
    marker.append('path').attr('d', 'M 0 0 L 10 5 L 0 10 z');

    var createMarkerBig = function(id) {
            return Viva.Graph.svg('marker')
                       .attr('id', id)
                       .attr('viewBox', "0 0 10 10")
                       .attr('refX', "10")
                       .attr('refY', "5")
                       .attr('markerUnits', "userSpaceOnUse")
                       .attr('markerWidth', "10")
                       .attr('markerHeight', "5")
                       .attr('orient', "auto");
        },
        markerBig = createMarkerBig('TriangleBig');
    markerBig.append('path').attr('d', 'M 0 0 L 10 5 L 0 10 z');
    // Marker should be defined only once in <defs> child element of root <svg> element:
    var defs = graphics.getSvgRoot().append('defs');
    defs.append(marker);
    defs.append(markerBig);
    var geom = Viva.Graph.geom();
    graphics.link(function(link) {
        var prev = graph.getNode(link.fromId);
        var prev_is_cluster = prev.data && prev.data.isCluster;
        var prev_cluster_name = prev_is_cluster ? parseInt(prev.id.split('-')[1]) : null;

        var to = graph.getNode(link.toId);
        var to_is_cluster = to.data && to.data.isCluster;
        var to_cluster_name = to_is_cluster ? parseInt(to.id.split('-')[1]) : null;

        var linked_to_cluster = prev_is_cluster || to_is_cluster;
        var cluster_to_cluster = prev_is_cluster && to_is_cluster;

        var color = '#aaa';

        var link_id = STATE.edges.indexOf(link.fromId + ',' + link.toId);
        if (linked_to_cluster) {
          link_id = -1;
        }

        var topics_perc = false;
        if (STATE.topics_per_edges && link_id !== -1) {
          var topic_max = -1;
          var topic_max_value = null;
          topics_perc = [];
          STATE.topics_per_edges.forEach((row, topic) => {
            var v = row[link_id];
            if (topic_max_value === null || v > topic_max_value) {
              topic_max_value = v;
              topic_max = topic;
            }
            topics_perc.push(v);
          });
          color = get_color(topic_max);

          // normalize topics_perc
          var sum = topics_perc.reduce(function(a, b) { return a + b; }, 0);
          topics_perc = topics_perc.map(x => x/sum);
        }

        var strokeWidth = 1;
        var cluster_topic_perc = false;
        if (cluster_to_cluster) {
          // BEST TOPIC
          cluster_topic_perc = STATE.theta_qr[
            to_cluster_name * Object.keys(STATE.clusterToNodes).length + prev_cluster_name];
          var topic_max = n_best_elems(cluster_topic_perc, 1)[0][0];
          color = get_color(topic_max);

          // WIDTH IN PI()
          var width = STATE.pi[prev_cluster_name][to_cluster_name];

          strokeWidth = 1 + 10*width;
        }

        var ui = Viva.Graph.svg('path')
                   .attr('stroke-width', strokeWidth)
                   .attr('fill', 'none')
                   .attr('stroke', color);
        
        if ((cluster_to_cluster || GRAPH.directed) && prev.id != to.id) {
          if (cluster_to_cluster) {
            ui.attr('marker-end', 'url(#TriangleBig)');
          } else {
            ui.attr('marker-end', 'url(#Triangle)');
          }
        }

        if (linked_to_cluster && !cluster_to_cluster) {
          ui.attr('stroke-dasharray', '5, 5');
        }

        $(ui).hover(function() {
          if (strokeWidth == 0) return;

          if (linked_to_cluster && !cluster_to_cluster) {
            return;
          }

          var words = [];

          if (link_id !== -1) {
            STATE.tdm.forEach(row => {
              row = row.map(x => parseInt(x));
              if (row[1] === link_id) {
                words.push(STATE.dictionnary[row[0]]);
              }
            });
          }

          ui.attr('stroke-width', strokeWidth + 2);
          renderGraphSidebar({
            title: ' ', // cluster_to_cluster ? prev.id + '→' + to.id : ' ',
            words,
            topics: topics_perc || cluster_topic_perc,
            topicsName: STATE.topicsName,
            renderer: RENDERER,
            pi_value: cluster_to_cluster ? STATE.pi[prev_cluster_name][to_cluster_name] : undefined,
            expand_clusters: expand_clusters.bind(this, graph, X, clusters),
            collapse_clusters: collapse_clusters.bind(this, graph, X, clusters),
          });
          renderGraphButtons({
            renderer: RENDERER,
            expand_clusters: expand_clusters.bind(this, graph, X, clusters),
            collapse_clusters: collapse_clusters.bind(this, graph, X, clusters),
            graph_layout_running: STATE.graph_layout_running,
            fit_graph: fit_graph,
          });
        }, function() {
          ui.attr('stroke-width', strokeWidth);
        });

        ui._prev = prev;
        ui._to = to;
        ui.cluster_to_cluster = cluster_to_cluster;

        return ui;
    }).placeLink(function(linkUI, fromPos, toPos) {
        // Here we should take care about
        //  "Links should start/stop at node's bounding box, not at the node center."
        // For rectangular nodes Viva.Graph.geom() provides efficient way to find
        // an intersection point between segment and rectangle
        var toNodeSize = linkUI._to._node_size + 1,
            fromNodeSize = linkUI._prev._node_size + 1;

        // self-loop
        if (fromPos.x == toPos.x && fromPos.y == toPos.y) {
          var x = fromPos.x - fromNodeSize / 2, y = fromPos.y;
          linkUI.attr("d", 'M ' + x + ' ' + y
              + ' c -30 -30 -30 30 0 0');
          return;
        }

        var from = geom.intersectRect(
                // rectangle:
                        fromPos.x - fromNodeSize / 2, // left
                        fromPos.y - fromNodeSize / 2, // top
                        fromPos.x + fromNodeSize / 2, // right
                        fromPos.y + fromNodeSize / 2, // bottom
                // segment:
                        fromPos.x, fromPos.y, toPos.x, toPos.y)
                   || fromPos; // if no intersection found - return center of the node
        var to = geom.intersectRect(
                // rectangle:
                        toPos.x - toNodeSize / 2, // left
                        toPos.y - toNodeSize / 2, // top
                        toPos.x + toNodeSize / 2, // right
                        toPos.y + toNodeSize / 2, // bottom
                // segment:
                        toPos.x, toPos.y, fromPos.x, fromPos.y)
                    || toPos; // if no intersection found - return center of the node
        var data = 'M' + from.x + ',' + from.y +
                   'L' + to.x + ',' + to.y;
        if (linkUI.cluster_to_cluster) {
          var ax = (to.x - from.x);
          var ay = (to.y - from.y)

          var mx = ax / 2 + from.x; // middle
          var my = ay / 2 + from.y;

          /*
          // find perpendicular line via dot product 
          0 = ax × bx + ay × by
          AX x bx = -AY x by
          bx = 1
          by = -AX/AY
          */

          var bx = ax > 0 ? 1 : -1;
          var by = - ax / ay;

          var b_length = Math.sqrt(bx*bx + by*by);
          var a_length = Math.sqrt(ax*ax * ay*ay);

          var px = mx + bx / b_length * 20;
          var py = my + by / b_length * 20;

          data = 'M ' + from.x + ' ' + from.y
              + ' Q ' + px + ' ' + py
              + ' ' + to.x + ' ' + to.y;
        }
        linkUI.attr("d", data);
    });
  return graphics;
}

init();

function update_graph_height() {
  var g = $('#_graph svg');
  g.height(window.innerHeight - g.offset().top - 20);
};
$(window).resize(update_graph_height);

var display_loading = () => {
  RENDERER.dispose();
  $('#_loading').text('Loading…');
  $('#_loading').show();
  renderGraphSidebar(null);
  renderGraphButtons(null);
}

export {
  init,
  display_loading,
  zoom_on,
};
