
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

function InService() {
  var service = document.getElementById("service").value;
  if (service == 0) {
    document.getElementById("service_start").style.display = "none";
  } else {
    document.getElementById("service_start").style.display = "block";
  }
}


function ChangementToothAnatomicLocation() {
  var anat_loc = document.getElementById("anatomic_location").value;
  var tooth = document.getElementById("tooth");
  var crown = document.getElementById("crown");
  var root = document.getElementById("root");
  var periodonte = document.getElementById("periodonte");

  if (anat_loc == 1 ) {
    tooth.style.display = "none";
    crown.style.display = "block";
    root.style.display = "none";
    periodonte.style.display = "none";
  } else if (anat_loc == 2 ) {
    tooth.style="display:none";
    crown.style="display:none";
    root.style="display:block";
    periodonte.style="display:none";
  } else if (anat_loc == 3 ) {
    tooth.style="display:none";
    crown.style="display:none";
    root.style="display:none";
    periodonte.style="display:block";
  } else {
    tooth.style="display:block";
    crown.style="display:none";
    root.style="display:none";
    periodonte.style="display:none";
  }
}

