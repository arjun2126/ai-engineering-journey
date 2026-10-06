(function () {
  "use strict";

  var form = document.getElementById("planner-form");
  var playerNameInput = document.getElementById("player-name");
  var goalInput = document.getElementById("goal");
  var durationInput = document.getElementById("duration");
  var submitButton = document.getElementById("submit-button");
  var spinner = submitButton.querySelector(".button-spinner");
  var errorPanel = document.getElementById("error-panel");
  var errorList = document.getElementById("error-list");
  var status = document.getElementById("status");
  var result = document.getElementById("result");
  var planTitle = document.getElementById("plan-title");
  var planMeta = document.getElementById("plan-meta");
  var planWarmup = document.getElementById("plan-warmup");
  var planDrills = document.getElementById("plan-drills");
  var planCues = document.getElementById("plan-cues");
  var againButton = document.getElementById("again-button");

  function selectedLevel() {
    var checked = form.querySelector('input[name="level"]:checked');
    return checked ? checked.value : "";
  }

  function setStatus(text, state) {
    status.textContent = text;
    if (state) {
      status.setAttribute("data-state", state);
    } else {
      status.removeAttribute("data-state");
    }
  }

  function showErrors(messages) {
    errorList.textContent = "";
    messages.forEach(function (message) {
      var item = document.createElement("li");
      item.textContent = message;
      errorList.appendChild(item);
    });
    errorPanel.hidden = false;
  }

  function hideErrors() {
    errorPanel.hidden = true;
    errorList.textContent = "";
  }

  function markInvalid(element, invalid) {
    if (invalid) {
      element.setAttribute("aria-invalid", "true");
    } else {
      element.removeAttribute("aria-invalid");
    }
  }

  function setLoading(loading) {
    submitButton.disabled = loading;
    spinner.hidden = !loading;
    form.setAttribute("aria-busy", loading ? "true" : "false");
  }

  function validate() {
    var messages = [];
    var name = playerNameInput.value.trim();
    var goal = goalInput.value.trim();
    var level = selectedLevel();
    var duration = Number(durationInput.value);

    var nameBad = name.length < 2;
    var goalBad = goal.length < 5;
    var levelBad = !level;
    var durationBad =
      durationInput.value.trim() === "" ||
      !Number.isInteger(duration) ||
      duration < 30 ||
      duration > 180;

    markInvalid(playerNameInput, nameBad);
    markInvalid(goalInput, goalBad);
    markInvalid(durationInput, durationBad);

    if (nameBad) {
      messages.push("Player name needs at least 2 characters.");
    }
    if (levelBad) {
      messages.push("Choose a level: beginner, intermediate, or advanced.");
    }
    if (goalBad) {
      messages.push("Training goal needs at least 5 characters.");
    }
    if (durationBad) {
      messages.push("Duration must be a whole number from 30 to 180 minutes.");
    }

    return {
      messages: messages,
      value: {
        player_name: name,
        level: level,
        goal: goal,
        duration_minutes: duration,
      },
    };
  }

  function apiDetailToMessages(body) {
    var detail = body && body.detail;
    if (typeof detail === "string" && detail) {
      return [detail];
    }
    if (Array.isArray(detail)) {
      return detail
        .map(function (entry) {
          if (typeof entry === "string") {
            return entry;
          }
          if (entry && typeof entry.msg === "string") {
            return entry.msg;
          }
          return "";
        })
        .filter(function (message) {
          return message !== "";
        });
    }
    return [];
  }

  function renderPlan(saved) {
    var content = saved.plan_content || {};
    var drills = Array.isArray(content.drills) ? content.drills : [];
    var cues = Array.isArray(content.coaching_cues)
      ? content.coaching_cues
      : [];

    if (!content.title || !content.warmup || drills.length === 0) {
      result.hidden = true;
      setStatus(
        "The plan came back empty. Try submitting the form again.",
        "error"
      );
      return;
    }

    planTitle.textContent = content.title;

    var metaParts = [];
    if (saved.level) {
      metaParts.push("Level: " + saved.level);
    }
    if (saved.duration_minutes !== undefined && saved.duration_minutes !== null) {
      metaParts.push(saved.duration_minutes + " minutes");
    }
    if (saved.player_name) {
      metaParts.push("Player: " + saved.player_name);
    }
    if (content.generator) {
      metaParts.push("Built with: " + content.generator);
    }
    planMeta.textContent = metaParts.join("  ·  ");

    planWarmup.textContent = content.warmup;

    planDrills.textContent = "";
    drills.forEach(function (drill) {
      var item = document.createElement("li");
      item.textContent = drill;
      planDrills.appendChild(item);
    });

    planCues.textContent = "";
    cues.forEach(function (cue) {
      var item = document.createElement("li");
      item.textContent = cue;
      planCues.appendChild(item);
    });

    result.hidden = false;
    setStatus("Your lesson plan is ready.", "success");
    planTitle.focus();
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    hideErrors();

    var checked = validate();
    if (checked.messages.length > 0) {
      showErrors(checked.messages);
      setStatus("Please fix the highlighted fields and try again.", "error");
      return;
    }

    setLoading(true);
    setStatus("Creating your lesson plan…", "loading");

    fetch("/lesson-plans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(checked.value),
    })
      .then(function (response) {
        if (!response.ok) {
          return response
            .json()
            .catch(function () {
              return {};
            })
            .then(function (body) {
              var messages = apiDetailToMessages(body);
              if (messages.length === 0) {
                messages = [
                  "The server returned an error (status " +
                    response.status +
                    "). Your entries were kept — try again.",
                ];
              }
              throw new Error(messages.join(" "));
            });
        }
        return response.json();
      })
      .then(function (saved) {
        renderPlan(saved);
      })
      .catch(function (error) {
        result.hidden = true;
        var message =
          error && error.message
            ? error.message
            : "Something went wrong. Your entries were kept — try again.";
        if (
          message.indexOf("Failed to fetch") !== -1 ||
          message.indexOf("NetworkError") !== -1 ||
          message.indexOf("Load failed") !== -1
        ) {
          showErrors([
            "Could not reach the server. Check your connection — your entries were kept.",
          ]);
          setStatus("Network error. Your entries were kept.", "error");
        } else {
          showErrors([message]);
          setStatus("Something went wrong. Your entries were kept.", "error");
        }
      })
      .finally(function () {
        setLoading(false);
      });
  });

  againButton.addEventListener("click", function () {
    result.hidden = true;
    hideErrors();
    setStatus("Your lesson plan will appear here once you submit the form.");
    playerNameInput.focus();
  });

  [playerNameInput, goalInput, durationInput].forEach(function (element) {
    element.addEventListener("input", function () {
      markInvalid(element, false);
    });
  });

  form
    .querySelectorAll('input[name="level"]')
    .forEach(function (radio) {
      radio.addEventListener("change", hideErrors);
    });
})();
