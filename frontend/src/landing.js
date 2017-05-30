
  // Sigma showcase in title:
  $.ajax({
    dataType: 'json',
    url: '/static/data/enron.json',
    success: function(graph) {
      var lines = 15,
          prefix = 'file_';

      // Sort nodes:
      graph.nodes = graph.nodes.sort(function(a, b) {
        return +(b.size - a.size) * 2 - 1;
      });

      // Set views:
      graph.nodes.forEach(function(node, i) {
        node.grid_x = 100 * (i % lines);
        node.grid_y = 100 * Math.floor(i / lines);
        node.grid_color = '#ccc';
        node.x = node.file_x = node.x;
        node.y = node.file_y = node.y;
        node.color = node.file_color = node.color;
      });

      // Initialize sigma:
      var s = new sigma({
        graph: graph,
        renderer: {
          container: document.getElementById('_graph-landing'),
          type: 'canvas'
        },
        settings: {
          enableCamera: false,
          enableHovering: false,
          mouseEnabled: false,
          drawLabels: false,
          animationsTime: 500
        }
      });

      function animate(p) {
        if (p !== prefix) {
          prefix = p || (prefix === 'grid_' ? 'file_' : 'grid_');
          sigma.plugins.animate(
            s,
            {
              color: prefix + 'color',
              x: prefix + 'x',
              y: prefix + 'y'
            }
          );
        }
      }

      var isDown = false,
          frameID;

      $('#_graph-landing').bind('mouseenter', function() {
        animate('grid_');
      }).bind('mouseleave', function() {
        animate('file_');
      }).bind('touchstart', function() {
        isDown = true;
        clearTimeout(frameID);
        frameID = setTimeout(function() {
          isDown = false;
        }, 100);
      }).bind('touchend', function() {
        if (isDown)
          animate();
        isDown = false;
      });
    }
  });
