function clock2() 
{
var time = new Date();
var secs = time.getSecondes();
var mins = time.getMinutes();
var hours = time.getHours();
var t = hours + ":" + mins + ":" + secs
setInterval({document.getElementById("clock").innerHTML=t}, 1000)
}

// Timer

var myVar = setInterval(function(){clock()}, 1000)

function clock()
{
var d=new Date();
var t=d.toLocaleTimeString();
document.getElementById("clock").innerHTML=t;
}
