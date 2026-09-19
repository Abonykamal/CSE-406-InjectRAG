/* Session, routing, login, and the two helpers everything else uses.
 *
 * Rendering safety rule for every file under web/: text that came from a
 * document or from the model reaches the DOM only through textContent or el().
 * There is no innerHTML anywhere here. Retrieved text is attacker-authored by
 * construction, so rendering it as HTML would put a live XSS hole in the
 * submission itself. */

var App = (function () {
  "use strict";

  var SESSION_KEY = "injectrag.session";
  var CHAT_KEY = "injectrag.chat";

  function getSession() {
    try {
      var raw = window.localStorage.getItem(SESSION_KEY);
      if (!raw) return null;
      var s = JSON.parse(raw);
      if (!s || typeof s !== "object" || !s.role || !s.username) return null;
      return s;
    } catch (e) {
      return null;
    }
  }

  function setSession(account) {
    try {
      window.localStorage.setItem(SESSION_KEY, JSON.stringify(account));
    } catch (e) { /* private mode: the session simply does not survive a reload */ }
  }

  function clearSession() {
    try {
      window.localStorage.removeItem(SESSION_KEY);
      window.localStorage.removeItem(CHAT_KEY);
    } catch (e) { /* nothing to clear */ }
  }

  function show(screenId) {
    var ids = ["screen-login", "screen-employee", "screen-technician"];
    ids.forEach(function (id) {
      var node = document.getElementById(id);
      if (node) node.hidden = id !== screenId;
    });
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function api(path, body) {
    return fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    }).then(function (res) {
      return res.text().then(function (raw) {
        var data = null;
        try { data = raw ? JSON.parse(raw) : null; } catch (e) { data = null; }
        if (!res.ok) {
          var detail = data && data.detail;
          if (Array.isArray(detail)) detail = detail.length ? detail[0].msg : null;
          var err = new Error(typeof detail === "string" ? detail : "Request failed");
          err.status = res.status;
          throw err;
        }
        return data;
      });
    });
  }

  /* Identity the server logs alongside each request. Not a credential: the
     server does not verify it, because authentication is out of scope here. */
  function identity() {
    var s = getSession() || {};
    return { user_id: s.user_id || "", username: s.username || "" };
  }

  function initials(display) {
    var parts = String(display || "").trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return "?";
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  function renderUserCard(node, session) {
    if (!node) return;
    node.textContent = "";
    node.appendChild(el("span", "avatar-user", initials(session.display)));
    var who = el("div", "who");
    who.appendChild(el("strong", null, session.display || session.username));
    who.appendChild(el("span", null, session.user_id || ""));
    node.appendChild(who);
  }

  function route() {
    var session = getSession();
    if (!session) {
      show("screen-login");
      var u = document.getElementById("login-username");
      if (u) u.focus();
      return;
    }
    if (session.role === "technician") {
      renderUserCard(document.getElementById("user-card-tech"), session);
      show("screen-technician");
      if (window.Cases) window.Cases.init(session);
      return;
    }
    renderUserCard(document.getElementById("user-card"), session);
    show("screen-employee");
    if (window.Chat) window.Chat.init(session);
  }

  function initLogin() {
    var form = document.getElementById("login-form");
    var username = document.getElementById("login-username");
    var password = document.getElementById("login-password");
    var button = document.getElementById("login-submit");
    var error = document.getElementById("login-error");

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      error.hidden = true;
      button.disabled = true;
      button.textContent = "";
      button.appendChild(el("span", "spinner"));

      api("/api/login", { username: username.value, password: password.value })
        .then(function (account) {
          setSession(account);
          password.value = "";
          route();
        })
        .catch(function (err) {
          error.textContent = err && err.status === 401
            ? "Incorrect username or password"
            : "Could not sign in. Please try again.";
          error.hidden = false;
          password.value = "";
          password.focus();
        })
        .then(function () {
          button.disabled = false;
          button.textContent = "Sign in";
        });
    });
  }

  function initLogout() {
    ["logout", "logout-tech"].forEach(function (id) {
      var node = document.getElementById(id);
      if (node) node.addEventListener("click", function () { clearSession(); route(); });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initLogin();
    initLogout();
    route();
  });

  return {
    CHAT_KEY: CHAT_KEY,
    api: api,
    el: el,
    identity: identity,
    initials: initials,
    getSession: getSession,
    clearSession: clearSession,
    route: route,
    show: show
  };
})();
