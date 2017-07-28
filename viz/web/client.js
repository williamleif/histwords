(function() {
  function submitTextarea() {
    var textEl = $(".input .inputbox");
    var promise = submitMessage(textEl.val(), function(data, res) {
      console.log("LOADED DATA!", data);
      $(".results").text(JSON.stringify(data, null, 2));


    });

    promise.fail(function() {
      promise.loadingcube.css("background-color", "#fdd");
    });

    promise.done(function() {
      console.log("LOADED RESULTS!");
    });


    textEl.val("");
  }

  function submitMessage(msg, cb) {
    // get the room we are in
    return getCmd("search", { term: msg}, cb);
  }

  function newLoading() {
    var loadingEl = $("<div class='loadingcube' ></div>");
    $(".loadingtray").append(loadingEl);
    loadingEl.fadeIn();
    loadingEl.done = function() {
      loadingEl.stop(true).fadeOut(function() {
        loadingEl.remove();
      });
    }
    return loadingEl;
  }

  function getCmd(cmd, data, cb) {
    var submit = _.clone(data);
    submit.cmd = cmd;
    loadingEl = newLoading();
    var ret= $.get("/r/", submit, function(data, res) {
      if (cb) { cb(data, res); }
    }).always(function() {
      loadingEl.done();
    });

    ret.loadingcube = loadingEl;
    return ret;

  }

  function postCmd(cmd, data, cb) {
    var submit = _.clone(data);
    submit.cmd = cmd;
    loadingEl = newLoading();
    var ret= $.post("/r/", submit, function(data, res) {
      if (cb) { cb(data, res); }
    }).always(function() {
      loadingEl.done();
    });

    ret.loadingcube = loadingEl;
    return ret;

  }


  // Gets ready to press enter
  function handleKeyDown(event) {
    if (event.keyCode == 13) {
        submitTextarea();
    }
  }

  $(function() {
    $(".input .inputbox").on("keydown", handleKeyDown);
  });

})();
