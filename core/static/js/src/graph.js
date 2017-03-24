import './graph/csrf.js';

import renderSidebar from './graph/sidebar';
import renderGraphSidebar from './graph/info';

import { hashedColor, COLORS, edgesArr, n_best_elems } from './graph/utils';
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

  STATE.labels = labels;
  STATE.n_edges = X.length;
  STATE.n_nodes = labels.length;
  STATE.dictionnary = dictionnary;
  STATE.edges = edgesArr(X);
  STATE.tdm = tdm;

  if (GRAPH.result && GRAPH.result.clusters_mat) {
    var nodeToCluster = Papa.parse(GRAPH.result.clusters_mat,
      {delimiter: ' ', dynamicTyping: true, skipEmptyLines: true}).data[0];

    if (nodeToCluster[0] === "") {
      nodeToCluster = nodeToCluster.slice(1);
    }

    var clusterToNodes = {};
    nodeToCluster.forEach(function(cluster, node) {
      if (!(cluster in clusterToNodes)) {
        clusterToNodes[cluster] = []
      }
      clusterToNodes[cluster].push(node);      
    });
    STATE.clusterToNodes = clusterToNodes;

    var topics = Papa.parse(GRAPH.result.topics_mat,
      {delimiter: '  ', dynamicTyping: true, skipEmptyLines: true}).data;

    topics.forEach((v, i) => {
      topics[i] = v.slice(1);
    });

    STATE.topicToTerms = topics;

    STATE.topicToTermsTFIDF = tfidf(topics);

    var topics_per_edges = Papa.parse(GRAPH.result.topics_per_edges_mat,
      {delimiter: '  ', dynamicTyping: true, skipEmptyLines: true}).data;

    topics_per_edges.forEach((v, i) => {
      topics_per_edges[i] = v.slice(1);
    });

    STATE.topics_per_edges = topics_per_edges;

    _add_clusters(graph, X, nodeToCluster)
  } else {
    X.forEach(function(line, i) {
      graph.addLink(line[0], line[1], {link_id: i});
    });
  }

  document.getElementById('_graph').innerHTML = '';

  RENDERER = Viva.Graph.View.renderer(graph, {
      container: document.getElementById('_graph'),
      graphics: get_graph_graphics(graph, X, nodeToCluster),
  });

  var loading = document.getElementById('_loading');
  if (loading) {
    document.getElementById('_loading').outerHTML = '';
  }

  RENDERER.run();
  setTimeout(function() {
    RENDERER.pause();
  }, 2000);

  renderSidebar(STATE);
  renderGraphSidebar({
    renderer: RENDERER,
    expand_clusters: expand_clusters.bind(this, graph, X, nodeToCluster),
    collapse_clusters: collapse_clusters.bind(this, graph, X, nodeToCluster),
  });
}

function expand_cluster(cluster_name, graph, X, clusters) {
  // remove current node
  graph.removeNode(cluster_name);

  // add all nodes of the cluster
  X.forEach(function(line, i) {
    // if origin node in cluster, add it
    if (clusters[line[0]] == cluster_name) {
      if (graph.getNode(line[1]) || clusters[line[1]] == cluster_name) {
        graph.addLink(line[0], line[1], {link_id: i});
      } else {
        // if target node not yet expanded, link to the cluster
        graph.addLink(line[0], clusters[line[1]]);
      }
    }
    // if target node in cluster, add it
    else if (clusters[line[1]] == cluster_name) {
      if (graph.getNode(line[0]) || clusters[line[0]] == cluster_name) {
        graph.addLink(line[0], line[1], {link_id: i});
      } else {
        // if origin node not yet expanded, link to the cluster
        graph.addLink(clusters[line[0]], line[1]);
      }
    }
  });
}

function expand_clusters(graph, X, clusters) {
  graph.clear()

  X.forEach(function(line, i) {
    graph.addLink(line[0], line[1], {link_id: i});
  });

  RENDERER.resume();
  setTimeout(function() {
    RENDERER.pause();
  }, 2000);
}

function _add_clusters(graph, X, nodeToCluster) {
  var added_links = new Set();
  X.forEach(function(line) {
    var cluster0 = nodeToCluster[line[0]];
    var cluster1 = nodeToCluster[line[1]];
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
    graph.addNode(cluster0, {isCluster: true});
    graph.addNode(cluster1, {isCluster: true});
    graph.addLink(cluster0, cluster1);
  });
}

function collapse_clusters(graph, X, clusters) {
  graph.forEachNode(function(node){
    graph.removeNode(node.id);
  });

  _add_clusters(graph, X, clusters);

  RENDERER.resume();
  setTimeout(function() {
    RENDERER.pause();
  }, 2000);
}

function get_graph_graphics(graph, X, clusters) {
    var graphics = Viva.Graph.View.svgGraphics(),
        nodeSize = 20;

    graphics.node(function(node) {
      var is_cluster = node.data && node.data.isCluster;

      var color = '#aaa';

      if (is_cluster) {
        color = hashedColor(node.id);
      }

      if (!is_cluster && clusters && clusters[node.id] !== undefined) {
        color = hashedColor(clusters[node.id]);
      }
      var ui = Viva.Graph.svg('g'),
          svgText = Viva.Graph.svg('text').attr('y', '-6px').text(node.id),
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
            .attr('x', -10)
            .attr('y', -10)
            .attr('width', 20)
            .attr('height', 20)
            .attr('style', 'fill: ' + color);
      // ui.append(svgText);
      if (is_cluster) {
        ui.append(square)
      } else {
        ui.append(circle);
      }

      svgText.attr('visibility', 'hidden');
      $(ui).hover(function() {
        // svgText.attr('visibility', 'visible');
        circle.attr('stroke-width', '1');

        renderGraphSidebar({
          title: node.data && node.data.isCluster ? node.id : STATE.labels[node.id],
          is_node: true,
          is_cluster: is_cluster,
          cluster: is_cluster || !clusters ? undefined : clusters[node.id],
          renderer: RENDERER,
          expand_clusters: expand_clusters.bind(this, graph, X, clusters),
          collapse_clusters: collapse_clusters.bind(this, graph, X, clusters),
        });
      }, function() {
        circle.attr('stroke-width', '0');
        // svgText.attr('visibility', 'hidden');
      });

      $(ui).click(function() {
        console.log('clicked on', node);
        if (is_cluster) {
          expand_cluster(node.id, graph, X, clusters);

          RENDERER.resume();
          setTimeout(function() {
            RENDERER.pause();
          }, 2000);
        }
      });

      return ui;
    }).placeNode(function(nodeUI, pos) {
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
                       .attr('markerUnits', "strokeWidth")
                       .attr('markerWidth', "10")
                       .attr('markerHeight', "5")
                       .attr('orient', "auto");
        },
        marker = createMarker('Triangle');
    marker.append('path').attr('d', 'M 0 0 L 10 5 L 0 10 z');
    // Marker should be defined only once in <defs> child element of root <svg> element:
    var defs = graphics.getSvgRoot().append('defs');
    defs.append(marker);
    var geom = Viva.Graph.geom();
    graphics.link(function(link) {
        var color = hashedColor('nopepp');

        var link_id = STATE.edges.indexOf(link.fromId + ',' + link.toId);
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
          color = hashedColor('t'+topic_max);
        }

        var ui = Viva.Graph.svg('path')
                   .attr('stroke-width', 0.5)
                   .attr('stroke', color);
        
        if (GRAPH.directed) {
          ui = ui.attr('marker-end', 'url(#Triangle)');
        }

        $(ui).hover(function() {
          var words = [];
          var topics_perc = [];

          /*
          goal: go from words to % of each topics

          for each word in document:
            for each topic:
              topics_perc[topic] += word_count*topic_word_perc
          */

          if (link_id !== -1) {
            STATE.tdm.forEach(row => {
              row = row.map(x => parseInt(x));
              if (row[1] === link_id) {
                words.push(STATE.dictionnary[row[0]]);
                if (STATE.topicToTerms) {
                  STATE.topicToTerms.forEach((terms, topic) => {
                    if (!topics_perc[topic]) {
                      topics_perc[topic] = 0;
                    }
                    topics_perc[topic] += row[2]*terms[row[0]];
                  })
                }
              }
            });

            // normalize topics_perc
            var sum = topics_perc.reduce(function(a, b) { return a + b; }, 0);
            topics_perc = topics_perc.map(x => x/sum);
            
          }

          ui.attr('stroke-width', 3);
          renderGraphSidebar({
            title: ' ',
            words,
            topics: topics_perc,
            renderer: RENDERER,
            expand_clusters: expand_clusters.bind(this, graph, X, clusters),
            collapse_clusters: collapse_clusters.bind(this, graph, X, clusters),
          });
        }, function() {
          ui.attr('stroke-width', 0.5);
        });

        return ui;
    }).placeLink(function(linkUI, fromPos, toPos) {
        // Here we should take care about
        //  "Links should start/stop at node's bounding box, not at the node center."
        // For rectangular nodes Viva.Graph.geom() provides efficient way to find
        // an intersection point between segment and rectangle
        var toNodeSize = nodeSize,
            fromNodeSize = nodeSize;
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
        linkUI.attr("d", data);
    });
  return graphics;
}

init();

export {
  init,
};
