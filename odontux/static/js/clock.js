function clock2() {
  var time = new Date();
  var mins = time.getMinutes();
  var hours = time.getHours();
  if (mins < 10) { mins = "0" + mins }
  if (hours < 10) { hours = "0" + hours }
  var t = hours + ":" + mins ;
  document.getElementsByTagName("time")[0].innerHTML=t;
}


