var stack = new Array();
var current;

$(document).ready(function() {
  $.getJSON('/tech/posts.json', function(json) {
    $.each(json, function(i, v) {
      v.fields.pk = v.pk;
      stack.push(v.fields);
    });
    next();
  });
});

function next() {
  current = stack.shift();
  $("td#post").html(current.title + " (" + current.source + ", " + current.date + ")");
}

function anchor() {
  window.open(current.link);
}

function dislike() {
  $.ajax({
    url: "/tech/" + current.pk + "/dislike",
    type: "PUT",
    success: function(data) {
      next();
    },
  });
}

function like() {
  $.ajax({
    url: "/tech/" + current.pk + "/like",
    type: "PUT",
    success: function(data) {
      next();
    },
  });
}

function BlockMove(event) { event.preventDefault(); }
