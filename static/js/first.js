function getWidth(flag) {
    if (flag) {
	var n_r = document.getElementById('name_role');
	var avatar = document.getElementById('avatar');
	var buttons = document.getElementById('settings_basket');
	var res = 1296 - avatar.clientWidth - n_r.clientWidth - buttons.clientWidth - 30;
	buttons.style.marginLeft = res + "px";
	}
}


function getHeightForComments(count) {
    for (var i = 1; i <= count; i++) {
        console.log(i);
        var div = document.getElementById('div-' + i);
        var h5 = document.getElementById('h5-' + i);
        div.style.height = div.clientHeight + h5.clientHeight / 2 + "px";
    }
}


function getMarginForProduct(cont_, button_, name_) {
	var cont = document.getElementById(cont_);
	var button = document.getElementById(button_);
	var name = document.getElementById(name_);
	var res = cont.clientHeight / 2 - button.clientHeight / 2;
	var res_1 = cont.clientHeight / 2 - name.clientHeight / 2;
	button.style.marginTop = res + "px";
	name.style.marginTop = res_1 + "px";
}

function getHeight(cont_, left_, right_) {
    var cont = document.getElementById(cont_);
	var left = document.getElementById(left_);
	var right = document.getElementById(right_);
    if (right.clientHeight > left.clientHeight) {
    cont.style.height = cont.clientHeight + right.clientHeight + 100 + "px";
    }
    else {
    cont.style.height = cont.clientHeight + left.clientHeight + 100 + "px";
    }
}
