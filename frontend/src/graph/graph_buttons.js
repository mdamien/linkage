import React from 'react';
import ReactDOM from 'react-dom';

function render(params) {
  if (params === null) {
    ReactDOM.render(<div></div>, document.getElementById('_graph-buttons'));
    return;
  }

  var buttons = <div style={{ position: 'absolute', bottom: 10, right: 10}}>
    {params.graph_layout_running ? <button href="#" className="btn btn-primary btn-xs" onClick={() => params.renderer.pause_in(0)}>pause auto-layout</button>
    : <button className="btn btn-primary btn-xs" onClick={() => params.renderer.clear_pause_in()}>resume auto-layout</button>}
    {GRAPH.magic_too_big_to_display_X || !params.meta_mode ? null : <span>&nbsp;<button href="#" className="btn btn-primary btn-xs" onClick={() => params.expand_clusters()}>expand clusters</button></span>}
    {GRAPH.magic_too_big_to_display_X || params.meta_mode ? null : <span>&nbsp;<button href="#" className="btn btn-primary btn-xs" onClick={() => params.collapse_clusters()}>collapse clusters</button></span>}
    &nbsp;
    {GRAPH.USE_EXPERIMENTAL_WEBGL_MODE ? null : <button href="#" className="btn btn-primary btn-xs" onClick={() => params.fit_graph()}>fit graph to view</button>}
  </div>;

  ReactDOM.render(buttons, document.getElementById('_graph-buttons'));
};

export default render;
