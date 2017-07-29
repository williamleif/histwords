(function() {
  var wordSettings = {
    frozenWord: null,
    freezeHighlight: false
  };

  // {{{ TABLE VIEW & CO
  function makeTableView(data, res) {
    makeMatrixByYear(data.results);
    // highlight words on hover
    $("table#matrix_by_year").find("td").on("mouseenter", function() {
      highlightDrift($(this).attr("data-word"), "compare");
    });
    $("table#matrix_by_year").find("td").on("mouseleave", function() {
      unhighlightDrift($(this).attr("data-word"), "compare");
    });
    // freeze highlight on click
    $("table#matrix_by_year").find("td").on("click", function() {
      freezeHighlightDrift($(this).attr("data-word"));
    });
  }

  function makeMatrixByYear(data) {
    var dataByYear = _.groupBy(data, "year");
    var $thisTable = $("table#matrix_by_year");
    $thisTable.empty();

    for (var year in dataByYear) {
      var arrWords = _.sortBy(dataByYear[year], "similarity").reverse();
      $thisTable.append("<tr class=\"flex-col\" id=\"year_" + year + "\"></tr>");
      $thisTable.find("#year_" +year+ "").append("<th>" + year + "</th>");
      for (var i = 0; i < arrWords.length; i++) {
        var similarity = Math.ceil(arrWords[i]["similarity"] * 100);
        $thisTable.find("#year_" + year + "")
          .append("<td data-word=\"cell-" + arrWords[i]["word"] + "\"" +
            "style=\"background-color: rgba(64,188,216, " + similarity / 100 + ")\">" +
            arrWords[i]["word"] + "<br/><span class=\"similarity\">" + similarity + "%</span></td>");
      }
    }
    $thisTable.show();
  }

  // Hover over word to highlight drift
  function highlightDrift(word, wordClass) {
    // highlght words with matching data-word attr
    $("table#matrix_by_year").find("td[data-word=\"" + word + "\"]").addClass(wordClass);
  }
  function unhighlightDrift(word, wordClass) {
    $("table#matrix_by_year").find("td[data-word=\"" + word + "\"]").removeClass(wordClass);
  }
  function freezeHighlightDrift(word) {
    if (wordSettings.freezeHighlight) {
      if (word === wordSettings.frozenWord) {
        wordSettings.freezeHighlight = false;
        wordSettings.frozenWord = null;
        unhighlightDrift(word, "selected");
      } else {
        unhighlightDrift(wordSettings.frozenWord, "selected");
        wordSettings.frozenWord = word;
        highlightDrift(word, "selected");
      }
    } else {
      wordSettings.freezeHighlight = true;
      highlightDrift(word, "selected");
      wordSettings.frozenWord = word;
    }
  }
  // }}} TABLE VIEW

  function submitTextarea() {
    var textEl = $(".header .inputbox");
    var word = textEl.val();

    textEl.attr("disabled", true);
    textEl.attr("placeholder", "searching for: " + word);

    var visualize = makeTableView;
    var promise = submitMessage(word, visualize);

    promise.fail(function() {
      promise.loadingcube.css("background-color", "#fdd");
    });

    promise.done(function() {
      textEl.attr("disabled", false);
      textEl.attr("placeholder", "enter a search term");
    });


    textEl.val("");
  }

  function submitMessage(msg, cb) {
    // get the room we are in
    return getCmd("search", { term: msg }, cb);
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
    $(".header .inputbox").on("keydown", handleKeyDown);
  });

})();
