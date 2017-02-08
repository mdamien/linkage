$.get('/result/' + GRAPH_ID + '/data/', function(full_data) {
  var graph = Viva.Graph.graph();

  var links = Papa.parse(full_data.links, {delimiter: ','}).data;
  links.forEach(function(line) {
    if (line[1]) { // not an empty line
      graph.addLink(line[0], line[1], line[2]);
    }
  });

  var nodeToCluster = {};
  var edgeToTopic = {};
  if (full_data.result && full_data.result.clusters) {
    var clusters = Papa.parse(full_data.result.clusters, {delimiter: ','}).data;
    clusters.forEach(function(line) {
      nodeToCluster[line[0]] = line[1];
    });

    var topics = Papa.parse(full_data.result.topics, {delimiter: ','}).data;
    topics.forEach(function(line) {
      edgeToTopic[line[0]+','+line[1]] = line[2];
    });
  }

  var layout = Viva.Graph.Layout.forceDirected(graph, {
      springLength : 10,
      springCoeff : 0.0005,
      dragCoeff : 0.02,
      gravity : -1.2
  });

  var renderer = Viva.Graph.View.renderer(graph, {
      container: document.getElementById('graph'),
      // layout: layout,
      graphics: get_graph_graphics(nodeToCluster, edgeToTopic),
  });
  renderer.run();
});

function get_graph_graphics(clusters, topics) {
    var COLORS = [
      '#1f77b4', '#aec7e8',
      '#ff7f0e', '#ffbb78',
      '#2ca02c', '#98df8a',
      '#d62728', '#ff9896',
      '#9467bd', '#c5b0d5',
      '#8c564b', '#c49c94',
      '#e377c2', '#f7b6d2',
      '#7f7f7f', '#c7c7c7',
      '#bcbd22', '#dbdb8d'
    ];

    var hashIt = function(s){
      return Math.abs(s.split("").reduce(function(a,b){a=((a<<5)-a)+b.charCodeAt(0);return a&a},0)) * 3423;
    }


    var graphics = Viva.Graph.View.svgGraphics(),
        nodeSize = 10;

    graphics.node(function(node) {
      var color = hashIt(node.id) % 2;
      if (clusters[node.id]) {
        color = hashIt(clusters[node.id]) % COLORS.length;
      }
      var ui = Viva.Graph.svg('g'),
          svgText = Viva.Graph.svg('text').attr('y', '-6px').text(node.id),
          circle = Viva.Graph.svg('circle')
            .attr('cx', 0)
            .attr('cy', 0)
            .attr('style', 'fill: ' + COLORS[color])
            .attr('r', 5);
      // ui.append(svgText);
      ui.append(circle);
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
    graphics.link(function(link){
        var color = hashIt(link.id) % 2 + 3;
        var topic = topics[link.fromId + ',' + link.toId];
        if (topic) {
          color = hashIt(topic) % COLORS.length;
        }
        // Notice the Triangle marker-end attribe:
        return Viva.Graph.svg('path')
                   .attr('stroke-width', 2)
                   .attr('stroke', COLORS[color])
                   .attr('marker-end', 'url(#Triangle)');
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
