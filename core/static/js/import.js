$('input[name="clustering"]').change(function() {
  var value = $(this).filter(':checked').val();
  $('._clustering-options').toggle(value == 'manual');
});
$('._clustering-options').hide();