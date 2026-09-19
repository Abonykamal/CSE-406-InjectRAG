/* Technician case entry.
 *
 * Filing a case puts its text into the corpus the assistant searches, which is
 * the ingestion channel the whole study is about. The UI says nothing about
 * that: it shows a reference number, the way any helpdesk would. Chunk counts
 * and corpus totals go to logs/ingestions.jsonl. */

window.Cases = (function () {
  "use strict";

  var el = App.el;
  var form, dateEl, titleEl, descEl, resEl, submitBtn, errorEl, resultEl;
  var wired = false;

  function today() {
    var d = new Date();
    var pad = function (n) { return String(n).padStart(2, "0"); };
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  }

  function reset() {
    form.reset();
    dateEl.value = today();
    errorEl.hidden = true;
    resultEl.hidden = true;
    resultEl.textContent = "";
    form.hidden = false;
    titleEl.focus();
  }

  function showResult(documentId) {
    resultEl.textContent = "";
    var line = el("p", "ref");
    line.appendChild(el("span", null, "✓ "));
    line.appendChild(el("strong", null, "Case filed"));
    line.appendChild(el("span", null, " — reference "));
    line.appendChild(el("strong", null, documentId));
    resultEl.appendChild(line);

    var again = el("button", "btn", "File another case");
    again.type = "button";
    again.addEventListener("click", reset);
    resultEl.appendChild(again);

    form.hidden = true;
    resultEl.hidden = false;
    again.focus();
  }

  function setBusy(busy) {
    submitBtn.disabled = busy;
    submitBtn.textContent = "";
    if (busy) {
      submitBtn.appendChild(el("span", "spinner"));
    } else {
      submitBtn.textContent = "Submit to knowledge base";
    }
  }

  function wire() {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      errorEl.hidden = true;

      var payload = {
        case_date: dateEl.value.trim(),
        title: titleEl.value.trim(),
        description: descEl.value.trim(),
        resolution: resEl.value.trim()
      };
      var missing = Object.keys(payload).some(function (k) { return !payload[k]; });
      if (missing) {
        errorEl.textContent = "Every field is required.";
        errorEl.hidden = false;
        return;
      }

      setBusy(true);
      App.api("/api/cases", Object.assign(payload, App.identity()))
        .then(function (data) {
          showResult((data && data.document_id) || "");
        })
        .catch(function (err) {
          // The typed content stays in the form.
          errorEl.textContent = (err && err.message) || "Could not file the case. Try again.";
          errorEl.hidden = false;
        })
        .then(function () {
          setBusy(false);
        });
    });
  }

  function init() {
    form = document.getElementById("case-form");
    dateEl = document.getElementById("case-date");
    titleEl = document.getElementById("case-title");
    descEl = document.getElementById("case-description");
    resEl = document.getElementById("case-resolution");
    submitBtn = document.getElementById("case-submit");
    errorEl = document.getElementById("case-error");
    resultEl = document.getElementById("case-result");
    if (!wired) { wire(); wired = true; }
    if (!dateEl.value) dateEl.value = today();
  }

  return { init: init };
})();
