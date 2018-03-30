import React from 'react';
import ReactDOM from 'react-dom';
import {Range} from 'rc-slider';
import Tooltip from 'rc-tooltip';

$('input[name="clustering"]').change(function() {
  var value = $(this).filter(':checked').val();
  $('._clustering-options').toggle(value == 'manual');
});
$('input[name="mbox_file"]').change(function() {
  $('._mbox-options').toggle(!!$(this).val());
});


class MyRange extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        min: 2,
        max: 5,
      };
    }
    render() {
      var {type} = this.props;

      var min = 2;
      var max = LINKAGE_ENTERPRISE ? 50 : 10
      var marks = {};
      for (var i = min; i <= max; i++) {
        if (i <= 10 || i % 5 == 0) marks[i] = i;
      }

      return <div>
        <div className="col-md-3 control-label">
          <strong>{type}</strong>
        </div>
        <div className="col-md-8">
          <input name={type + '_min'} type="hidden" value={this.state.min}/>
          <input name={type + '_max'} type="hidden" value={this.state.max}/>
          <Range steps={1} dots defaultValue={[2, 5]}
            count={2}
            min={min}
            max={max}
            marks={marks}
            onAfterChange={(v) => {this.setState({min: v[0], max:v[1]})}}/>
        </div>
      </div>;
    }
};

ReactDOM.render(<MyRange type={'topics'}/>, document.getElementById('_slider_topics'));
ReactDOM.render(<MyRange type={'clusters'}/>, document.getElementById('_slider_clusters'));
