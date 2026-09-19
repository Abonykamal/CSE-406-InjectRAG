/* Employee chat.
 *
 * An assistant turn contains the answer text and nothing else: no sources, no
 * scores, no condition label, no marker banner. That is the point of the build --
 * the attack has to be visible as ordinary helpdesk advice, and the evidence for
 * it lives in logs/queries.jsonl, not on screen. */

window.Chat = (function () {
  "use strict";

  var el = App.el;
  var transcript, emptyState, form, input, sendBtn;
  var session = null;
  var inflight = false;
  var wired = false;

  function loadHistory() {
    try {
      var raw = window.localStorage.getItem(App.CHAT_KEY);
      var list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list.filter(function (m) {
        return m && typeof m.content === "string" && (m.role === "user" || m.role === "assistant");
      }) : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistory(list) {
    try {
      window.localStorage.setItem(App.CHAT_KEY, JSON.stringify(list));
    } catch (e) { /* history is a convenience, never required */ }
  }

  function appendHistory(role, content) {
    var list = loadHistory();
    list.push({ role: role, content: content });
    saveHistory(list);
  }

  function setEmptyVisible(visible) {
    if (emptyState) emptyState.hidden = !visible;
  }

  function scrollToEnd() {
    transcript.scrollTop = transcript.scrollHeight;
  }

  function avatar(role) {
    if (role === "user") {
      return el("span", "avatar-user", App.initials(session && session.display));
    }
    var bot = el("span", "avatar-bot");
    bot.textContent = "◆";
    return bot;
  }

  /* One message row. `body` is a node so a placeholder can be swapped in place. */
  function addRow(role, bodyNode) {
    var row = el("div", "msg msg-" + role);
    row.appendChild(avatar(role));
    var body = el("div", "msg-body");
    body.appendChild(bodyNode);
    row.appendChild(body);
    transcript.appendChild(row);
    setEmptyVisible(false);
    scrollToEnd();
    return body;
  }

  function typingNode() {
    var t = el("div", "typing");
    t.appendChild(el("span"));
    t.appendChild(el("span"));
    t.appendChild(el("span"));
    return t;
  }

  function setBody(body, node) {
    body.textContent = "";
    body.appendChild(node);
    scrollToEnd();
  }

  function setInflight(busy) {
    inflight = busy;
    sendBtn.disabled = busy || !input.value.trim();
  }

  function autoGrow() {
    input.style.height = "auto";
    var wanted = input.scrollHeight;
    input.style.height = Math.min(wanted, 200) + "px";
    // Only show a scrollbar once the box has actually stopped growing.
    input.style.overflowY = wanted > 200 ? "auto" : "hidden";
  }

  function failure(body, question) {
    var wrap = el("div", "msg-error");
    wrap.appendChild(el("p", "banner banner-danger", "Couldn't send that. Try again."));
    var retry = el("button", "btn", "Retry");
    retry.type = "button";
    retry.addEventListener("click", function () {
      if (inflight) return;
      var row = body.parentNode;
      if (row && row.parentNode) row.parentNode.removeChild(row);
      ask(question);
    });
    wrap.appendChild(retry);
    setBody(body, wrap);
    // The question is never silently lost.
    input.value = question;
    autoGrow();
    input.focus();
  }

  function ask(question) {
    var body = addRow("assistant", typingNode());
    setInflight(true);
    App.api("/api/chat", Object.assign({ question: question }, App.identity()))
      .then(function (data) {
        var answer = (data && data.answer) || "";
        setBody(body, document.createTextNode(answer));
        appendHistory("assistant", answer);
      })
      .catch(function () {
        failure(body, question);
      })
      .then(function () {
        setInflight(false);
      });
  }

  function submit(question) {
    question = (question || "").trim();
    if (!question || inflight) return;
    addRow("user", document.createTextNode(question));
    appendHistory("user", question);
    input.value = "";
    autoGrow();
    ask(question);
  }

  function replay() {
    transcript.textContent = "";
    transcript.appendChild(emptyState);
    var list = loadHistory();
    list.forEach(function (m) {
      addRow(m.role === "user" ? "user" : "assistant", document.createTextNode(m.content));
    });
    setEmptyVisible(list.length === 0);
    scrollToEnd();
  }

  function newChat() {
    saveHistory([]);
    replay();
    input.value = "";
    autoGrow();
    input.focus();
  }

  function wire() {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      submit(input.value);
    });

    input.addEventListener("input", function () {
      autoGrow();
      sendBtn.disabled = inflight || !input.value.trim();
    });

    input.addEventListener("keydown", function (ev) {
      if (ev.key === "Enter" && !ev.shiftKey) {
        ev.preventDefault();
        submit(input.value);
      }
    });

    Array.prototype.forEach.call(
      document.querySelectorAll("#screen-employee .suggestion"),
      function (b) {
        b.addEventListener("click", function () {
          input.value = b.textContent;
          autoGrow();
          submit(input.value);
        });
      }
    );

    var newBtn = document.getElementById("new-chat");
    if (newBtn) newBtn.addEventListener("click", newChat);
  }

  function init(activeSession) {
    session = activeSession;
    transcript = document.getElementById("transcript");
    emptyState = document.getElementById("empty-state");
    form = document.getElementById("composer");
    input = document.getElementById("question");
    sendBtn = document.getElementById("send");
    if (!wired) { wire(); wired = true; }
    replay();
    autoGrow();
    setInflight(false);
    input.focus();
  }

  return { init: init };
})();
