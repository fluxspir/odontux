window.onload = function() {

  // On page load : reset values and hide input forms
  document.getElementById( "anamnesis_type" ).value = 2;
  document.getElementById( "medical_history" ).style.display = "block";
  document.getElementById( "addiction" ).style.display = "none";
  document.getElementById( "treatment" ).style.display = "none";
  document.getElementById( "past_surgery" ).style.display = "none";
  document.getElementById( "allergy" ).style.display = "none";
}
