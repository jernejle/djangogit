pn = window.location.pathname.split("/")

function setEvents() {
	$(".tree").click(function() {
		$(".table > tbody").empty();
		Dajaxice.repocontrol.getobjects(Dajax.process,{'userid':pn[1],'slug':pn[2], 'sha':$(this).attr('id')})
	});
	$(".blob").click(function() {
		$(".table").remove()
		Dajaxice.repocontrol.getBlob(Dajax.process,{'userid':pn[1],'slug':pn[2], 'sha':$(this).attr('id')})
	});
}

function writeBlob(data) {
	$(".files").html(data)
}

function test(data) {
	alert(data)
}

function getDiff() {
	Dajaxice.repocontrol.getCommitDiff(Dajax.process,{'userid':pn[1],'slug':pn[2], 'sha':sha})
}

function writeDiff(data) {
	$("#commitdiff").html(data)
}
