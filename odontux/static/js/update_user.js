var obj = null ;

function display_form(id) {
  if (obj) {
    obj.style.visibility = "hidden" ;
    obj.style.zIndex = "1" ;
  }
  obj = document.getElementById(id) ;
  obj.style.visibility = "visible" ;
  obj.style.zIndex = "20" ;
}

