/* Show time in general_info bar */
function clock2() {
  var time = new Date();
  var mins = time.getMinutes();
  var hours = time.getHours();
  if (mins < 10) { mins = "0" + mins }
  if (hours < 10) { hours = "0" + hours }
  var t = hours + ":" + mins ;
  document.getElementById("clock").innerHTML=t;
}

function clock() {
  var d=new Date();
  var t=d.toLocaleTimeString();
  document.getElementById("clock").innerHTML=t;
}

/* Menu déroulant du user */
// function to open hidden layer
var ddmenuitem = 0;
var closetimer = 0;
var timeout = 1000;

function mopen(id) {
  mcancelclosetime(); // cancel close timer
  if (ddmenuitem) ddmenuitem.style.visibility="hidden"; // close old layer
  // get new layer and show it
  ddmenuitem = document.getElementById(id);
  ddmenuitem.style.visibility="visible";
}
// Close showed layer
function mclose() {
  if (ddmenuitem) ddmenuitem.style.visibility = "hidden";
}
// go close timer
function mclosetime() {
  closetimer = window.setTimeout(mclose, timeout);
}
// cancel close timer
function mcancelclosetime() {
  if (closetimer) {
    window.clearTimeout(closetimer);
    closetimer = null;
  }
}
