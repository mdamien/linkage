import renderSidebar from './graph/sidebar';
import renderGraphSidebar from './graph/info';

import { hashedColor, COLORS } from './graph/utils';

// TODO: STATE is here to keep computed things in memory, could be cleaned up
var STATE = {};

var graph = Viva.Graph.graph();

var links = Papa.parse(GRAPH.links, {delimiter: ','}).data;
console.log('links:', links.length);

STATE.n_edges = links.length;

var nodes = new Set();
links.forEach(function(line) {
  if (line[1]) { // not an empty line
    nodes.add(line[0]);
    nodes.add(line[1]);
  }
});
STATE.n_nodes = nodes.size;

var nodeToCluster = {};
var edgeToTopic = {};

if (GRAPH.result && GRAPH.result.clusters) {
  var clusters = Papa.parse(GRAPH.result.clusters, {delimiter: ','}).data;
  var clusterToNodes = {};
  clusters.forEach(function(line) {
    var cluster = line[1];
    if (cluster) {
      nodeToCluster[line[0]] = cluster;

      if (!(cluster in clusterToNodes)) {
        clusterToNodes[cluster] = []
      }
      clusterToNodes[cluster].push(line[0]);      
    }
  });
  STATE.clusterToNodes = clusterToNodes;

  var topicToEdgesPercentage = null;
  var topics = Papa.parse(GRAPH.result.topics, {delimiter: ','}).data;
  topics.forEach(function(line) {
    var percentages = line.slice(2).map(function(v){
      return parseFloat(v);
    });
    edgeToTopic[line[0]+','+line[1]] = percentages;
    if (topicToEdgesPercentage == null) {
      topicToEdgesPercentage = percentages;
    } else {
      percentages.forEach((v, i) => {
        topicToEdgesPercentage[i] += v;
      });
    }
  });
  STATE.topicToEdgesPercentage = topicToEdgesPercentage;

  STATE.topicToTerms = Papa.parse(GRAPH.result.topics_terms, {delimiter: ','}).data;

  links.forEach(function(line) {
    if (line[1]) { // not an empty line
      var cluster0 = nodeToCluster[line[0]] || line[0];
      var cluster1 = nodeToCluster[line[1]] || line[1];
      graph.addLink(cluster0, cluster1);
    }
  });
} else {
  links.forEach(function(line) {
    if (line[1]) { // not an empty line
      graph.addLink(line[0], line[1], line[2]);
    }
  });
}

var layout = Viva.Graph.Layout.forceDirected(graph, {
    springLength : 100,
    springCoeff : 0.0005,
    dragCoeff : 0.02,
    gravity : -1.0
});

var RENDERER = Viva.Graph.View.renderer(graph, {
    container: document.getElementById('_graph'),
    // layout: layout,
    graphics: get_graph_graphics(graph, links, nodeToCluster, edgeToTopic),
});

document.getElementById('_loading').outerHTML = '';

RENDERER.run();
setTimeout(function() {
  RENDERER.pause();
}, 2000);

renderSidebar(STATE);
renderGraphSidebar({
  renderer: RENDERER,
});

function get_graph_graphics(graph, links, clusters, topics) {
    var graphics = Viva.Graph.View.svgGraphics(),
        nodeSize = 10;

    graphics.node(function(node) {
      var color = hashedColor(node.id);
      if (clusters[node.id]) {
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
            .attr('r', 5),
          square = Viva.Graph.svg('rect')
            .attr('stroke', 'black')
            .attr('stroke-width', '0')
            .attr('x', -5)
            .attr('y', -5)
            .attr('width', 10)
            .attr('height', 10)
            .attr('style', 'fill: ' + color);
      // ui.append(svgText);
      if (STATE.clusterToNodes && node.id in STATE.clusterToNodes) {
        ui.append(square)
      } else {
        ui.append(circle);
      }

      svgText.attr('visibility', 'hidden');
      $(ui).hover(function() {
        // svgText.attr('visibility', 'visible');
        circle.attr('stroke-width', '1');
        renderGraphSidebar({
          title: node.id,
          is_node: true,
          cluster: clusters[node.id],
          renderer: RENDERER,
        });
      }, function() {
        circle.attr('stroke-width', '0');
        // svgText.attr('visibility', 'hidden');
      });

      $(ui).click(function() {
        console.log('clicked on', node);
        if (STATE.clusterToNodes && node.id in STATE.clusterToNodes) {
          // remove current node
          graph.removeNode(node.id);

          // add all nodes of the cluster
          links.forEach(function(line) {
            if (line[1]) { // not an empty line
              // if origin node in cluster, add it
              if (clusters[line[0]] == node.id) {
                if (graph.getNode(line[1]) || clusters[line[1]] == node.id) {
                  graph.addLink(line[0], line[1], line[2]);
                } else {
                  // if target node not yet expanded, link to the cluster
                  graph.addLink(line[0], clusters[line[1]], line[2]);
                }
              }
              // if target node in cluster, add it
              else if (clusters[line[1]] == node.id) {
                if (graph.getNode(line[0]) || clusters[line[0]] == node.id) {
                  graph.addLink(line[0], line[1], line[2]);
                } else {
                  // if origin node not yet expanded, link to the cluster
                  graph.addLink(clusters[line[0]], line[1], line[2]);
                }
              }
            }
          });

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
        var topic = topics[link.fromId + ',' + link.toId];
        if (topic) {
          var idx_max = topic.indexOf(Math.max.apply(Math, topic))
          color = hashedColor(''+idx_max);
        }

        var ui = Viva.Graph.svg('path')
                   .attr('stroke-width', 2)
                   .attr('stroke', color)
                   .attr('marker-end', 'url(#Triangle)');

        $(ui).hover(function() {
          ui.attr('stroke-width', 3);
          renderGraphSidebar({
            title: link.data,
            topics: topics[link.fromId + ',' + link.toId],
            renderer: RENDERER,
          });
        }, function() {
          ui.attr('stroke-width', 2);
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


var socket = new WebSocket("ws://" + window.location.host + '/result/' + GRAPH.id + '/');
socket.onmessage = function(e) {
  location.reload();
}
socket.onopen = function() {

}
// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();