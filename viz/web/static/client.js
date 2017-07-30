(function() {
  var SELECTED_VIEW = "table";
  var DATA, RES;

  // {{{ JSON VIEW
  function makeJsonView(data, res) {
    $(".results").empty();
    $(".results").append(
      $("<pre />").text(JSON.stringify(data, null, 2))
    );


  }
  // }}}

  // {{{ table view & co
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

    var resultEl = $(".results");
    resultEl.empty();

    var $thisTable = $("<table />")
      .attr('id', "matrix_by_year")
      .addClass("flex");

    resultEl.append($thisTable);

    var dataByYear = _.groupBy(data, "year");
    for (var year in dataByYear) {
      var arrWords = _.sortBy(dataByYear[year], "similarity").reverse();
      $thisTable.append("<tr class=\"flex-col\" id=\"year_" + year + "\"></tr>");
      $thisTable.find("#year_" +year+ "").append("<th>" + year + "</th>");
      _.each(arrWords, function(word) {
        var similarity = Math.ceil(word.similarity * 100);
        var wordColor = getColor(word.query);
        wordColor.opacity = similarity / 100;


        var tdEl = $("<td />");
        tdEl.attr("data-word", "cell-" + word.word);

        tdEl.css("background-color", wordColor);
        tdEl.text(word.word);
        tdEl.append("<br />");
        tdEl.append($("<span />").addClass("similarity").text(similarity + "%"));
        tdEl.attr("title", word.query + " ");
        $thisTable.find("#year_" + year + "")
          .append(tdEl);


      });
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

  var wordSettings = {
    frozenWord: null,
    freezeHighlight: false
  };

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

  // {{{ word cloud plot
  var scale = d3.schemeCategory10;
  function getColor(term) {
    if (getColor.colors[term] == null) {
      getColor.idx++;
      getColor.colors[term] = scale[getColor.idx % scale.length];
    }


    return d3.color(getColor.colors[term]);
  }
  getColor.colors = {}
  getColor.idx = 0;

  function makeCloudView(data, res) {
    $(".results").empty();

    var results = _.filter(data.results, function(d) { return !d.query.includes(d.word) ; } );
    var annotations = _.filter(data.results, function(d) { return d.query.includes(d.word) ; } );
    annotations = _.sortBy(annotations, function(d) { return d.year; } );

    var groupedAnns = _.groupBy(annotations, function(d) { return d.word; });

    var ann_lines = {}
    _.each(groupedAnns, function(annotations, group) {
      var ann_line = [];
      var prevAnn;
      _.each(annotations, function(ann) {
        if (prevAnn) {
          ann_line.push([prevAnn.position.x, prevAnn.position.y, ann.position.x, ann.position.y ]);
        }
        prevAnn = ann;
      });

      ann_lines[group] = ann_line;
    });



    var scaleFactor = 10;

    function getPos(min_or_max, x_or_y) {
      var val = _[min_or_max](results, function(d) { return d.position[x_or_y];});
      return parseInt(val.position[x_or_y] * scaleFactor, 10);
    }

    // normalize the results positions...
    var minX = getPos('min', 'x');
    var maxX = getPos('max', 'x');
    var minY = getPos('min', 'y');
    var maxY = getPos('max', 'y');

    var resultEl = d3.select(".results")
      .append("svg")
      .attr("viewBox", [minX - 25, minY - 25, maxX - minX + 50, maxY - minY + 50].join(" "))
      .attr("width", "100%")
      .attr("height", "100%");

    resultEl
      .selectAll("text.term")
      .data(results)
      .enter()
      .append("text")
        .style("font-size", function(d) { return parseInt(d.similarity * scaleFactor, 10) + "px";})
        .style("cursor", "pointer")
        .attr("x", function(d) { return d.position.x * scaleFactor; })
        .attr("y", function(d) { return d.position.y * scaleFactor; })
        .attr("fill", function(d) { return getColor(d.query); })
        .style("opacity", function(d) { return Math.max(0.1, (d.year - 1800) / 200); })
        .text(function(d) { return d.word; })
        .append("title")
          .text(function(d) { return d.query + " " + d.year });

    _.each(ann_lines, function(ann_line, group) {
      resultEl
        .selectAll("line.annotation")
        .data(ann_line)
        .enter()
        .append("line")
          .style("stroke", getColor(group))
          .style("stroke-width", "1.5px")
          .style("opacity", 0.3)
          .attr("x1", function(d) { return d[0] * scaleFactor; })
          .attr("y1", function(d) { return d[1] * scaleFactor; })
          .attr("x2", function(d) { return d[2] * scaleFactor; })
          .attr("y2", function(d) { return d[3] * scaleFactor; })
          .append("title")
            .text(group);
    });

    resultEl
      .selectAll("text.annotation")
      .data(annotations)
      .enter()
      .append("text")
        .style("font-size", "3px")
        .style("cursor", "pointer")
        .attr("x", function(d) { return d.position.x * scaleFactor + 1; })
        .attr("y", function(d) { return d.position.y * scaleFactor + 1; })
        .text(function(d) { return d.year; });

  }

  // }}}

  // {{{ server communications
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
  // }}} server comm

  // {{{ vis picker
  var VIZ = {
    "table" : makeTableView,
    "cloud" : makeCloudView,
    "json" : makeJsonView
  };

  function getCrumb(term) {
    return term.replace(/:/g, "_");
  }

  function visualizeResults(data, res) {
    DATA = data;
    RES = res;

    // highlight the term from data
    $(".breadcrumb").removeClass("active");
    $("#breadcrumb_" + getCrumb(data.term)).addClass("active");

    drawVisuals();
  }

  function drawVisuals() {
    var visualize = VIZ[SELECTED_VIEW];
    visualize(DATA, RES);
  }
  // }}}

  // {{{ text area handler
  function searchTerm(word) {
    var textEl = $(".header .inputbox");

    textEl.attr("disabled", true);
    textEl.attr("placeholder", "searching for: " + word);

    var promise = submitMessage(word, visualizeResults);

    promise.fail(function() {
      promise.loadingcube.css("background-color", "#fdd");
    });

    promise.done(function() {
      textEl.attr("disabled", false);
      textEl.attr("placeholder", "enter a search term");
    });


    textEl.val("");
  }

  function addBreadcrumb(word) {
    var breadCrumbEl = $("#breadcrumb_"+getCrumb(word));
    if (!breadCrumbEl.length) {
      breadCrumbEl = $("<div />");
      breadCrumbEl.addClass("breadcrumb");
      breadCrumbEl.attr("id", "breadcrumb_" + getCrumb(word));
      breadCrumbEl.text(word);
      $(".breadcrumbs").prepend(breadCrumbEl);
      breadCrumbEl.on("click", function() {
        searchTerm(word);
      });
    }
  }

  function submitTextarea() {
    var textEl = $(".header .inputbox");
    var word = textEl.val();

    addBreadcrumb(word);
    searchTerm(word);
  }


  // Gets ready to press enter
  function handleKeyDown(event) {
    if (event.keyCode == 13) {
        submitTextarea();
    }
  }

  $(function() {
    $(".header .inputbox").on("keydown", handleKeyDown);
    viewtabBoxEl = $(".viewtab_box");
    _.each(VIZ, function(func, viz) {
      console.log("VIZ", viz);
      var el = $("<div class='viewtab' />");
      el.text(viz)
        .data("viz", viz);

      if (viz == SELECTED_VIEW) {
        el.addClass("active");
      }

      viewtabBoxEl.append(el);

      // click handler for viewtab
      el.on("click", function(el) {
        SELECTED_VIEW = $(this).data("viz");
        $(".viewtab").removeClass("active");
        $(this).addClass("active");
        drawVisuals();
      });
    });

  });
  // }}} text area handler

})();
