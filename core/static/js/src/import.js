$('input[name="clustering"]').change(function() {
  var value = $(this).filter(':checked').val();
  $('._clustering-options').toggle(value == 'manual');
});
$('input[name="mbox_file"]').change(function() {
  $('._mbox-options').toggle(!!$(this).val());
});
