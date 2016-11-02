 
 
$(function () {

  var today = new Date();

  var set_default_asset_category = function() {
    document.getElementById( "brand" ).value = null;
    $('#commercial_name').val(null);
    $('#description').val(null);
    $('#asset_specialty_id').val(null);
    $('#is_sterilizable').val(null);
    $('#sterilization_validity').val(null);
  }
  var set_default_asset = function() {
    $('#acquisition_date').val(today.getFullYear()+"-"+(today.getMonth()+1)+"-"+today.getDate() );
    $('#acquisition_price').val(null);
    $('#new').prop('checked', true);
    $('#quantity').val(null);
    }
  var set_default_device_category = function() {
  }
  var set_default_device = function() {
    $('#lifetime_expected').val(null);
  }
  var set_default_material_category = function() {
    $('#unity').val(1);
    $('#initial_quantity').val(null);
    $('#automatic_decrease').val(null);
    $('#order_threshold').val(null);
  }
  var set_default_material = function() {
    $('#batch_number').val(null);
    $('#expiration_date').val(null);
    $('#expiration_alert').val(null);
    $('#service').prop('checked', false);
    $('#start_of_use').val(today.getFullYear()+"-"+(today.getMonth()+1)+"-"+today.getDate() );
  }

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
        set_default_asset_category();
        document.getElementById( "asset" ).style.display = "block";
        set_default_asset();
        set_default_device_category();
        set_default_device();
        document.getElementById( "material_category" ).style.display = "block";
        set_default_material_category();
        document.getElementById( "material" ).style.display = "block";
        set_default_material();
        document.getElementById( "add_the_asset" ).style.display = "block";
      } else {
      document.getElementById( "type" ).value = data.type;
      document.getElementById( "asset_type" ).style.display = "block";
      document.getElementById( "asset_category" ).style.display = "block";
      document.getElementById( "brand" ).value = data.brand;
      document.getElementById( "commercial_name" ).value = data.commercial_name;
      $('#description').val(data.description);
      $('#asset_specialty_id').val(data.asset_specialty_id);
      $('#is_sterilizable').val(data.is_sterilizable);
      $('#sterilization_validity').val(data.sterilization_validity);
      document.getElementById( "asset" ).style.display = "block";
      set_default_asset();
      set_default_device();
      set_default_material();
      if ( data.type == "device" ) {
        $('#device_category').show();
        $('#device').show();
        $('#material_category').hide();
        $('#material').hide();
      } else {
        $('#device_category').hide();
        $('#device').hide();
        $('#material_category').show();
        $('#material').show();
        $('#order_threshold').val(data.order_threshold);
        $('#unity').val(data.unity);
        $('#initial_quantity').val(data.initial_quantity);
        $('#automatic_decrease').val(data.automatic_decrease);
        }

        document.getElementById( "add_the_asset" ).style.display = "block";
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
