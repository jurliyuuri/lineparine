function toggle(isJietoden)
{
	var arr = document.getElementsByClassName("Fynelipa");
	for(var i=0; i<arr.length; i++) {
		arr[i].style.fontFamily = isJietoden ? "Fynelipa" : "Times New Roman";
	}
}
