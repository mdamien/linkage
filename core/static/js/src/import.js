$('input[name="clustering"]').change(function() {
  var value = $(this).filter(':checked').val();
  $('._clustering-options').toggle(value == 'manual');
});
$('._clustering-options').hide();

$('input[name="mbox_file"]').change(function() {
  $('._mbox-options').toggle(!!$(this).val());
});
$('._mbox-options').hide();