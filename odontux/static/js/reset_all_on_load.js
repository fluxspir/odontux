window.onload = function() {

  // On page load : reset values and hide input forms
  document.getElementById( "barcode" ).value = "";
  document.getElementById( "asset_type" ).style.display = "none";
  document.getElementById( "asset_category" ).style.display = "none";
  document.getElementById( "device_category" ).style.display = "none";
  document.getElementById( "material_category" ).style.display = "none";
  document.getElementById( "asset" ).style.display = "none";
  document.getElementById( "device" ).style.display = "none";
  document.getElementById( "material" ).style.display = "none";
  document.getElementById( "add_the_asset" ).style.display = "none";
}
