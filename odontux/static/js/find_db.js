 
 
$(function () {
  var submit_barcode = function() {
    $.getJSON($SCRIPT_ROOT + '/test_barcode/', {
      barcode: $('input[name="barcode"]').val(),
    }, function(data) {
      if (data.success == false) {
        //$("#result").val(document.getElementById("barcode").value)
        //$("#result2").text("Ce code n'est pas dans db");
        document.getElementById( "type" ).value = "material";
        document.getElementById( "asset_type" ).style.display = "block";
        document.getElementById( "asset_category" ).style.display = "block";
        document.getElementById( "asset" ).style.display = "block";
        document.getElementById( "material_category" ).style.display = "block";
        document.getElementById( "material" ).style.display = "block";
        document.getElementById( "add_the_asset" ).style.display = "block";
      } else {
      $("#result").text(data.brand);
      }
    });
    return false;
  };

  // a click on this will launch function "submit_barcode" above
  $('a#verify_barcode').bind('click', submit_barcode);

//$('input[type=text]').bind('keydown', function(e) {
  //  if (e.keycode == 13) {
  //    submit_barcode(e);
  //  }
  //});
});
