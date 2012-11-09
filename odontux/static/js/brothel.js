function clock2() 
{
var time = new Date();
//var mins = time.getMinutes();
var mins = 5
var hours = time.getHours();
/**/
var l = [hours, mins];
for (k in l) { 
  if (0 <= k && k <10) { 
    k = "0" + k 
  } 
}
/**/
//if (0 <= mins && mins < 10) { mins = "0" + mins }
//if (0 <= hours && hours < 10) { hours = "0" + hours }
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
obj.innerHTML= username + "<br /><a href='/logout/'>Logout</a><br />"
}

function usermenuout(obj)
{

}
