/* Employee chat.
 *
 * An assistant turn contains the answer text and nothing else: no sources, no
 * scores, no condition label, no marker banner. That is the point of the build --
 * the attack has to be visible as ordinary helpdesk advice, and the evidence for
 * it lives in logs/queries.jsonl, not on screen.
 *
 * A conversation is purely client-side: history is never sent, and the server
 * holds no thread state, so the same question asked in a new chat is identical
 * server-side. That is what makes "ask it again with the defense on" a clean
 * comparison. Each conversation carries an id (logged, so the pair of runs can
 * be found) and a generation token (so a reply from a conversation the employee
 * has already left is discarded rather than landing in the new one). */

window.Chat = (function () {
  "use strict";

  var el = App.el;
  var transcript, emptyState, form, input, sendBtn;
  var session = null;
  var inflight = false;
  var wired = false;
  var conversationId = null;
  /* Bumped by newChat(). A reply whose token no longer matches is dropped. */
  var generation = 0;
  var bar, defenseSel, corpusSel, lockNote;

  function newConversationId() {
    return "c-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
  }

  /* The selects are live only before a conversation's first message: one
     condition per chat, which is the comparison the demo is built around.
     Changing it mid-thread would make the transcript unreadable as evidence. */
  function setLocked(locked) {
    if (!bar || bar.hidden) return;
    if (defenseSel) defenseSel.disabled = locked;
    if (corpusSel) corpusSel.disabled = locked;
    if (lockNote) lockNote.hidden = !locked;
  }

  function applyConfig(cfg) {
    bar = document.getElementById("demo-bar");
    defenseSel = document.getElementById("demo-defense");
    corpusSel = document.getElementById("demo-corpus");
    lockNote = document.getElementById("demo-locked");
    if (!bar) return;
    bar.hidden = !cfg.controls;
    if (!cfg.controls) return;
    if (defenseSel) defenseSel.value = cfg.defense;
    if (corpusSel) corpusSel.value = cfg.corpus;
    setLocked(loadHistory().length > 0);
  }

  /* What this conversation runs under. Omitted entirely when the controls are
     off, so the server falls back to its own configuration. */
  function conditionFields() {
    var cfg = App.config();
    if (!cfg.controls) return {};
    return {
      defense: defenseSel ? defenseSel.value : cfg.defense,
      corpus: corpusSel ? corpusSel.value : cfg.corpus
    };
  }

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
    var token = generation;
    setInflight(true);
    if (!conversationId) conversationId = newConversationId();
    var payload = Object.assign(
      { question: question, conversation_id: conversationId },
      App.identity(),
      conditionFields()
    );
    App.api("/api/chat", payload)
      .then(function (data) {
        // The employee started a new chat while this was in flight. The answer
        // belongs to a conversation that no longer exists on screen -- showing
        // it, or writing it to history, would attribute it to the new one.
        if (token !== generation) return;
        var answer = (data && data.answer) || "";
        setBody(body, document.createTextNode(answer));
        appendHistory("assistant", answer);
      })
      .catch(function () {
        if (token !== generation) return;
        failure(body, question);
      })
      .then(function () {
        if (token !== generation) return;
        setInflight(false);
      });
  }

  function submit(question) {
    question = (question || "").trim();
    if (!question || inflight) return;
    addRow("user", document.createTextNode(question));
    appendHistory("user", question);
    setLocked(true);
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
    // Invalidate anything still in flight before clearing, so a late reply from
    // the previous conversation cannot land in this one.
    generation += 1;
    inflight = false;
    conversationId = newConversationId();
    saveHistory([]);
    replay();
    setLocked(false);
    input.value = "";
    autoGrow();
    setInflight(false);
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
    if (!conversationId) conversationId = newConversationId();
    transcript = document.getElementById("transcript");
    emptyState = document.getElementById("empty-state");
    form = document.getElementById("composer");
    input = document.getElementById("question");
    sendBtn = document.getElementById("send");
    if (!wired) { wire(); wired = true; }
    replay();
    applyConfig(App.config());
    autoGrow();
    setInflight(false);
    input.focus();
  }

  return { init: init, applyConfig: applyConfig };
})();
