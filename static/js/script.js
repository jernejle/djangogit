pn = window.location.pathname.split("/")

function setEvents() {
	$(".tree").click(function() {
		$(".table > tbody").empty();
		Dajaxice.repocontrol.getobjects(Dajax.process, {
			'userid' : pn[1],
			'slug' : pn[2],
			'sha' : $(this).attr('id')
		})
	});
	$(".blob").click(function() {
		$(".table").remove()
		Dajaxice.repocontrol.getBlob(Dajax.process, {
			'userid' : pn[1],
			'slug' : pn[2],
			'sha' : $(this).attr('id')
		})
	});
}

function writeBlob(data) {
	$(".files").html(data)
}

function test(data) {
	alert(data)
}

function getDiff() {
	Dajaxice.repocontrol.getCommitDiff(Dajax.process, {
		'userid' : pn[1],
		'slug' : pn[2],
		'sha' : sha
	})
}

function writeDiff(data) {
	$("#commitdiff").html(data)
}

function postIssue(data) {
	if (data != "") {
		if (data.length > 0) {
			for (var i = 0; i < data.length; i++) {
				var datespl = data[i].date.split(" ")
				var timespl = datespl[1].split(".")
				if (!data[i].open) {
					var top = "<div class='issue-top'><i class='icon-lock'></i> <a href='/" + data[i].href + "'>" + data[i].title + "</a></div>"
				} else {
					var top = "<div class='issue-top'><a href='/" + data[i].href + "'>" + data[i].title + "</a></div>"
				}
				var bottom = "<div class='issue-bottom'><b>" + data[i].author + "</b> on " + datespl[0] + " at " + timespl[0].substr(0, 5) + " <span class='issue-type'>" + data[i].label + "</span></div>"
				$("#issues").append(top)
				$("#issues").append(bottom)
			}
		}
	}
}