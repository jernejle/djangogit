pn = window.location.pathname.split("/")

function setEvents() {
	$(".tree").click(function() {
		$(".table > tbody").empty();
		Dajaxice.repocontrol.getobjects(Dajax.process, {
			'userid' : pn[1],
			'slug' : pn[2],
			'sha' : $(this).attr('id')
		});
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
	if (data != "") {
		var inhtml = "<pre class='linenums'><code>" + data + "</code></pre>"
		$(".files").html(inhtml)
		styleCode()
	} else {
		$(".files").remove()
	}
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
				if (data[i].deadline != "None") {
					deadline = "<span style='float: right'><i class='icon-fire'></i> " + data[i].deadline + "</span>"
				} else {
					deadline = ""
				}
				if (!data[i].open) {
					var top = "<div class='issue-top'><i class='icon-lock'></i> <a href='/" + data[i].href + "'>" + data[i].title + "</a>" + deadline +"</div>"
				} else {
					if (data[i].label == "Bug") {
						la = "<i class='icon-exclamation-sign'></i>"
					} else if (data[i].label == "Question") {
						la = "<i class='icon-question-sign'></i>"
					} else if (data[i].label == "Enhancement") {
						la = "<i class='icon-leaf'></i>"
					}

					if (data[i].deadline != "None") {
						deadline = "<span style='float: right'><i class='icon-fire'></i> " + data[i].deadline + "</span>"
					} else {
						deadline = ""
					}
					var top = "<div class='issue-top'>" + la + "&nbsp;<a href='/" + data[i].href + "'>" + data[i].title + "</a>" + deadline + "</div>"
				}
				var bottom = "<div class='issue-bottom'><i class='icon-user'></i>&nbsp;<b>" + data[i].author + "</b> on " + datespl[0] + " at " + timespl[0].substr(0, 5) + " <span class='issue-type'>" + data[i].label + "</span></div>"
				$("#issues").append(top)
				$("#issues").append(bottom)
			}
		}
	}
}

function commitcomment(data) {
	$("#spinner").remove()
	if (data.length > 0) {
		for (var i = 0; i < data.length; i++) {
			var div = "<div class='indexrow'><i class='icon-comment'></i>&nbsp;<a href='/users/viewprofile/" + data[i].author_id + "/'>" + data[i].author_username + "</a> commented <a href='/" + data[i].userid + "/" + data[i].slug + "/commit/" + data[i].sha + "/'>commit #" + data[i].sha.substr(0, 5) + "</a> in <a href='/" + data[i].userid + "/" + data[i].slug + "/'>" + data[i].repo_user + "/" + data[i].slug + "</a><span style='float: right'>" + data[i].date + "</span></div>";
			$(data[i].tab).append(div)
		}
		$(data[0].tab).append("<hr />")
	}
}

function issues(data) {
	$("#spinner").remove()
	if (data.length > 0) {
		for (var i = 0; i < data.length; i++) {
			var datespl = data[i].date.split(" ")
			var timespl = datespl[1].split(".")
			var la = "<div class='indexrow'>"
			if (data[i].label == "1") {
				la += "<i class='icon-exclamation-sign'></i>"
			} else if (data[i].label == "3") {
				la += "<i class='icon-question-sign'></i>"
			} else if (data[i].label == "2") {
				la += "<i class='icon-leaf'></i>"
			}
			la += "&nbsp;<a href='/users/viewprofile/" + data[i].author_id + "/'>" + data[i].author_username + "</a> oppened new <a href='" + data[i].userid + "/" + data[i].slug + "/issues/" + data[i].id + "/'>issue</a> in <a href='" + data[i].userid + "/" + data[i].slug + "/'>" + data[i].repo_user + "/" + data[i].slug + "</a><span style='float:right'>" + data[i].date + "</span></div>";
			$(data[i].tab).append(la)
		}
		$(data[0].tab).append("<hr />")
	}
}

function issuescomments(data) {
	$("#spinner").remove()
	if (data.length > 0) {
		for (var i = 0; i < data.length; i++) {
			var datespl = data[i].date.split(" ")
			var timespl = datespl[1].split(".")

			var div = "<div class='indexrow'><i class='icon-comment'></i>&nbsp;<a href='/users/viewprofile/" + data[i].author_id + "/'>" + data[i].author_username + "</a> commented on <a href='/" + data[i].userid + "/" + data[i].slug + "/issues/" + data[i].id + "/'>issue</a> in <a href='/" + data[i].userid + "/" + data[i].slug + "/'>" + data[i].repo_user + "/" + data[i].slug + "</a><span style='float: right'>" + data[i].date + "</span></div>";
			$(data[i].tab).append(div)
		}
		$(data[0].tab).append("<hr />")
	}
}

function newrepos(data) {
	if (data.length > 0) {
		for (var i = 0; i < data.length; i++) {
			var datespl = data[i].date.split(" ")
			var timespl = datespl[1].split(".")

			var div = "<div class='indexrow'><i class='icon-book'></i>&nbsp;<a href='/users/viewprofile/" + data[i].author_id + "/'>" + data[i].author_username + "</a> created new repository <a href='/" + data[i].author_id + "/" + data[i].slug + "/'>" + data[i].author_username + "/" + data[i].slug + "</a><span style='float: right'>" + data[i].date + "</span></div>"
			$(data[i].tab).append(div)
		}
	}
}

function styleCode() {
	if ( typeof disableStyleCode != "undefined") {
		return;
	}

	var a = false;

	$("pre code").parent().each(function() {
		if (!$(this).hasClass("prettyprint")) {
			$(this).addClass("prettyprint");
			a = true
		}
	});

	if (a) {
		prettyPrint()
	}
}