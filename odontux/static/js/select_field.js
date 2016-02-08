

function ChangementType() {
  var type = document.getElementById("type").value;
  var device_category = document.getElementById("device_category");
  var device = document.getElementById("device");
  var material_category = document.getElementById("material_category");
  var material = document.getElementById("material");

  if (type == "device") {
    device_category.style="display:block";
    device.style="display:block";
    material_category.style="display:none";
    material.style="display:none";
  } else {
    device_category.style="display:none";
    device.style="display:none";
    material_category.style="display:block";
    material.style="display:block";
  }
}

