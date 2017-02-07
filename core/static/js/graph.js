$.get('/result/' + GRAPH_ID + '/data/', function(csv) {
  var data = Papa.parse(csv).data;
  console.log(data);

  // var graphGenerator = Viva.Graph.generator();
  // var graph = graphGenerator.wattsStrogatz(150, 4, 0.2);

  var graph = Viva.Graph.graph();
  data.forEach(function(line) {
    if (line[1]) { // not an empty line
      graph.addLink(line[0], line[1], line[2]);
    }
  });

  var graphics = Viva.Graph.View.svgGraphics(),
      nodeSize = 10;

  var layout = Viva.Graph.Layout.forceDirected(graph, {
      springLength : 10,
      springCoeff : 0.0005,
      dragCoeff : 0.02,
      gravity : -1.2
  });

  graphics.node(function(node) {
    var ui = Viva.Graph.svg('g'),
        svgText = Viva.Graph.svg('text').attr('y', '-6px').text(node.id),
        circle = Viva.Graph.svg('circle')
          .attr('cx', 0)
          .attr('cy', 0)
          .attr('style', 'fill: #efb73e')
          .attr('r', 5);
    ui.append(svgText);
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
      // Notice the Triangle marker-end attribe:
      return Viva.Graph.svg('path')
                 .attr('stroke', 'gray')
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

  var renderer = Viva.Graph.View.renderer(graph, {
      container: document.getElementById('graph'),
      layout: layout,
      graphics: graphics,
  });
  renderer.run();
});
