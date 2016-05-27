
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
  var anat_loc_val = document.getElementById("anatomic_location").value;
  var tooth = document.getElementById("tooth");
  var crown = document.getElementById("crown");
  var root = document.getElementById("root");
  var periodonte = document.getElementById("periodonte");

  if (anat_loc_val == 1 ) {
    tooth.style.display = "none";
    crown.style.display = "block";
    root.style.display = "none";
    periodonte.style.display = "none";
  } else if (anat_loc_val == 2 ) {
    tooth.style="display:none";
    crown.style="display:none";
    root.style="display:block";
    periodonte.style="display:none";
  } else if (anat_loc_val == 3 ) {
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

function ChangementAnamnesisType() {
  var anamnesis_val = document.getElementById("anamnesis_type").value;
  var medical_history = document.getElementById("medical_history");
  var addiction = document.getElementById("addiction");
  var treatment = document.getElementById("treatment");
  var past_surgery = document.getElementById("past_surgery");
  var allergy = document.getElementById("allergy");
  var oral_hygiene = document.getElementById("oral_hygiene");

  if ( anamnesis_val == 1 ) {
    medical_history.style.display = "block";
    addiction.style.display = "none";
    treatment.style.display = "none";
    past_surgery.style.display = "none";
    allergy.style.display = "none";
    oral_hygiene.style.display = "none";
  } else if ( anamnesis_val == 2) {
    medical_history.style.display = "none";
    addiction.style.display = "block";
    treatment.style.display = "none";
    past_surgery.style.display = "none";
    allergy.style.display = "none";
    oral_hygiene.style.display = "none";
  } else if ( anamnesis_val == 3) {
    medical_history.style.display = "none";
    addiction.style.display = "none";
    treatment.style.display = "block";
    past_surgery.style.display = "none";
    allergy.style.display = "none";
    oral_hygiene.style.display = "none";
  } else if ( anamnesis_val == 4) {
    medical_history.style.display = "none";
    addiction.style.display = "none";
    treatment.style.display = "none";
    past_surgery.style.display = "block";
    allergy.style.display = "none";
    oral_hygiene.style.display = "none";
  } else if (anamnesis_val == 5) {
    medical_history.style.display = "none";
    addiction.style.display = "none";
    treatment.style.display = "none";
    past_surgery.style.display = "none";
    allergy.style.display = "block";
    oral_hygiene.style.display = "none";
  } else if (anamnesis_val == 6) {
    medical_history.style.display = "none";
    addiction.style.display = "none";
    treatment.style.display = "none";
    past_surgery.style.display = "none";
    allergy.style.display = "none";
    oral_hygiene.style.display = "block";
  } else {
    medical_history.style.display = "none";
    addiction.style.display = "none";
    treatment.style.display = "none";
    past_surgery.style.display = "none";
    allergy.style.display = "none";
    oral_hygiene.style.display = "none";
  }
}
