import React from 'react';
import ReactDOM from 'react-dom';
import Cookies from 'js-cookie';

var csrftoken = Cookies.get('csrftoken');

function render() {
  var jobs = JOBS.map((job, i) => {
    return <div className='panel panel-default' key={i}>
      <div className='panel-heading'>{job.name}</div>
      <div className='panel-body'>
        <div className='row'>
          <div className='col-md-5'>
            <div><em>Auto-clustering between 2 and 10 topics and 2 and 10 clusters</em></div>
            <div>Est. time to process: <strong>3h30</strong> (~<strong>1h05</strong> left)</div>
          </div>
          <div className='col-md-7 text-right'>
            <form method='post'>
              <input type='hidden' name='csrfmiddlewaretoken' value={csrftoken}/>
              <input type='hidden' name='action' value='delete'/>
              <input type='hidden' name='graph_id' value={job.id}/>
              <a className='btn btn-success' href={job.url}>View</a>
              &nbsp;&nbsp;&nbsp;&nbsp;
              <a className='btn btn-info' href={job.url+'details/'}>Details</a>
              &nbsp;&nbsp;&nbsp;&nbsp;
              <button className='btn btn-danger' type='submit'>Delete</button>
            </form>
          </div>
        </div>
        <div className='row'>
          <div className="col-md-12">
              <br/>
              <div className="progress progress-striped active">
                  <div className="progress-bar" style={{width: '45%'}}></div>
              </div>
              <pre style={{maxHeight: 100}}>{job.log}</pre>
          </div>
        </div>
      </div>
    </div>;
  });
  ReactDOM.render(<div>{jobs}</div>, document.getElementById('_jobs'));
};

if (JOBS.length > 0) {
  render();
}
