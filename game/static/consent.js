initialize("/game/api/status/", "GET", (status) => {
	function chooseAvatar() {
		if ($("select").val()==1) {$("#img-avatar").attr('src', '/static/user1C.svg');}
		if ($("select").val()==2) {$("#img-avatar").attr('src', '/static/user2C.svg');}
		if ($("select").val()==3) {$("#img-avatar").attr('src', '/static/user3C.svg');}
		if ($("select").val()==4) {$("#img-avatar").attr('src', '/static/user4C.svg');}
	}
	function loadAvatar() {
		if (status.avatar==1) {$("#img-avatar").attr('src', '/static/user1C.svg');}
		if (status.avatar==2) {$("#img-avatar").attr('src', '/static/user2C.svg');}
		if (status.avatar==3) {$("#img-avatar").attr('src', '/static/user3C.svg');}
		if (status.avatar==4) {$("#img-avatar").attr('src', '/static/user4C.svg');}
	}
	chooseAvatar();
	loadAvatar();
	$("select").on('change', chooseAvatar);
});