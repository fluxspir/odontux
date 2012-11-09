function clock2() 
{
var time = new Date();
var mins = time.getMinutes();
var mins = 5
var hours = time.getHours();
/**/
var l = [hours, mins];
for (var i=0 ; i <2 ; i++) { 
  if (0 <= l[i] && l[i] <10) { 
    l[i] = "0" + l[i];
  } 
}
/**//*
if (0 <= mins && mins < 10) { mins = "0" + mins }
if (0 <= hours && hours < 10) { hours = "0" + hours }*/
var t = hours + ":" + mins ;
document.getElementById("clock").innerHTML=t;
}

function clock()
{
var d=new Date();
var t=d.toLocaleTimeString();
document.getElementById("clock").innerHTML=t;
}

function usermenuover(obj, username)
{
document.getElementById("userhidden").style.visibility="visible";
obj.style.fontSize = "120%" ;
obj.style.backgroundColar = "green";
}

function usermenuout(obj, username)
{
document.getElementById("userhidden").style.visibility="hidden";
obj.style.fontSize = "100%";
obj.style.backgroundColar = "green";
}
