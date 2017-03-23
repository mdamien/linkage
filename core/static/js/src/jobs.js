import React from 'react';
import ReactDOM from 'react-dom';
import Cookies from 'js-cookie';

var csrftoken = Cookies.get('csrftoken');

function render() {
  if (JOBS.length == 0) return;
  var jobs = JOBS.map((job, i) => {
    var finished = job.progress == 1;
    return <div className='panel panel-default' key={i}>
      <div className='panel-heading'>{job.name}</div>
      <div className='panel-body'>
        <div className='row'>
          <div className='col-md-5'>
            <div>
              {job.job_param_topics != job.job_param_topics_max || job.job_param_clusters != job.job_param_clusters_max ?
                <em>
                  Auto-clustering between {job.job_param_topics} to {job.job_param_topics_max} topics
                  {' '}and {job.job_param_clusters} to {job.job_param_clusters_max} clusters
                </em> :
                <em>Clustering with {job.job_param_topics} topics and {job.job_param_clusters} clusters</em>
              }
            </div>
            <div>Created: {job.created_at}</div>
            {finished ?
              <div>Took <strong>{job.time.toFixed(2)}s</strong></div> :
              null // <div>Est. time to process: <strong>3h30</strong> (~<strong>1h05</strong> left)</div>
            }
          </div>
          <div className='col-md-7 text-right'>
            <form method='post'>
              <input type='hidden' name='csrfmiddlewaretoken' value={csrftoken}/>
              <input type='hidden' name='action' value='delete'/>
              <input type='hidden' name='graph_id' value={job.id}/>
              {finished ? <span>
                <a className='btn btn-success' href={job.url}>View</a>
                &nbsp;&nbsp;&nbsp;&nbsp;
                <a className='btn btn-warning' href={job.url+'details/'}>Details</a>
                &nbsp;&nbsp;&nbsp;&nbsp;
              </span> : null}
              <button className='btn btn-danger' type='submit'>Delete</button>
            </form>
          </div>
        </div>
        <div className='row'>
          <div className="col-md-12">
              <br/>
              {finished ? null : <div className="progress progress-striped active">
                  <div className="progress-bar" style={{width: '10%'}}></div>
              </div>}
              <div>Log:</div>
              <pre style={{maxHeight: 100}}>{job.log}</pre>
              {/*<pre style={{maxHeight: 100}}>{JSON.stringify(job, null, 2)}</pre>*/}
          </div>
        </div>
      </div>
    </div>;
  });
  ReactDOM.render(<div>{jobs}</div>, document.getElementById('_jobs'));
};


var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var socket = new WebSocket(ws_scheme + "://" + window.location.host + '/jobs/');

socket.onmessage = function(e) {
  console.log(e);
  $.getJSON('/jobs/', {
    as_json: true,
  }, function(data) {
    JOBS = data;
    render();
  });
}

// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();

render();
