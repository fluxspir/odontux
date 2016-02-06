

function ChangementType() {
  var type = document.getElementById("type").value;
  var device = document.getElementById("device_category");
  var material = document.getElementById("material_category");

  if (type == "device_category") {
    device.style="display:block";
    material.style="display:none";
  } else {
    device.style="display:none";
    material.style="display:block";
  }
}

