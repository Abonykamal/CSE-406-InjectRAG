"use strict";

const $ = (id) => document.getElementById(id);
const api = async (path, options) => {
  const r = await fetch(path, options);
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(body.detail || `${r.status} ${r.statusText}`);
  return body;
};
const post = (path, data) =>
  api(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data || {}),
  });

const el = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text; // never innerHTML
  return n;
};

// --- status --------------------------------------------------------------

function renderStatus(s) {
  const attackers = s.attacker_documents.length;
  $("status-bar").textContent =
    `Corpus: ${s.documents} documents (${attackers} attacker-submitted), ` +
    `${s.chunks} chunks · provider: ${s.provider} · marker: ${s.marker}`;
}

const refreshStatus = () => api("/api/status").then(renderStatus);

// --- tabs ----------------------------------------------------------------

const TABS = { chat: null, tickets: loadTickets, corpus: loadCorpus };
for (const name of Object.keys(TABS)) {
  $(`tab-${name}`).addEventListener("click", () => {
    for (const other of Object.keys(TABS)) {
      $(`tab-${other}`).classList.toggle("active", other === name);
      $(`panel-${other}`).classList.toggle("hidden", other !== name);
    }
    if (TABS[name]) TABS[name]();
  });
}

// --- chat ----------------------------------------------------------------

function renderTurn(data) {
  const turn = el("div", "turn");
  turn.appendChild(el("p", "q", data.question));

  if (data.marker_present) {
    turn.appendChild(el("div", "banner danger",
      `MARKER DETECTED — the answer contains "${data.marker}". The injection succeeded.`));
  } else if (data.attacker_in_context) {
    turn.appendChild(el("div", "banner ok",
      "Attacker content was retrieved into the context, but the answer does not carry the marker."));
  }
  if (data.fallback_reason) {
    turn.appendChild(el("div", "banner warn",
      `Live provider failed; answered by the offline fake provider instead. ${data.fallback_reason}`));
  }

  turn.appendChild(el("p", "a", data.answer || "(empty answer)"));

  const meta = el("div", "meta");
  meta.appendChild(el("div", null,
    `condition=${data.condition} · defense=${data.defense} · ` +
    `${data.provider}/${data.model} · finish=${data.finish_reason}`));
  meta.appendChild(el("div", null,
    `retrieval: attacker_in_topk=${data.attacker_in_topk} · ` +
    `attacker_in_context=${data.attacker_in_context}`));
  turn.appendChild(meta);

  const sources = el("div");
  sources.appendChild(el("strong", null, "Retrieved sources"));
  for (const s of data.sources) {
    sources.appendChild(el("div", `src ${s.membership}`,
      `${s.rank}. [${s.document_id}] ${s.title} — score ${s.score.toFixed(4)}` +
      (s.membership === "attacker" ? "  ← attacker-submitted" : "")));
  }
  turn.appendChild(sources);

  const details = el("details");
  details.appendChild(el("summary", null, "Exactly what was sent to the model"));
  details.appendChild(el("pre", null,
    `--- SYSTEM ---\n${data.system_prompt}\n\n--- USER ---\n${data.user_message}`));
  turn.appendChild(details);

  $("transcript").prepend(turn);
}

$("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = $("question").value.trim();
  if (!question) return;
  const button = e.target.querySelector("button");
  button.disabled = true;
  button.textContent = "Thinking…";
  try {
    const data = await post("/api/chat", { question, defense: $("defense").value });
    renderTurn(data);
    renderStatus(data.corpus);
    $("question").value = ""; // cleared only on success
  } catch (err) {
    $("transcript").prepend(el("div", "banner danger", `Request failed: ${err.message}`));
  } finally {
    button.disabled = false;
    button.textContent = "Ask";
    $("question").focus();
  }
});

// --- tickets -------------------------------------------------------------

let payloads = [];

async function loadPayloads() {
  payloads = (await api("/api/attack-payloads")).payloads;
  const picker = $("payload-picker");
  for (const p of payloads) {
    const opt = el("option", null, `Load attacker payload ${p.document_id}`);
    opt.value = p.document_id;
    picker.appendChild(opt);
  }
}

$("payload-picker").addEventListener("change", (e) => {
  const p = payloads.find((x) => x.document_id === e.target.value);
  if (!p) return;
  $("ticket-subject").value = p.subject;
  $("ticket-description").value = p.employee_description;
  $("role").value = "attacker";
});

async function loadTickets() {
  const { tickets } = await api("/api/tickets");
  const list = $("ticket-list");
  list.textContent = "";
  if (!tickets.length) {
    list.appendChild(el("p", "meta", "No tickets yet."));
    return;
  }
  for (const t of tickets) {
    const card = el("div", "ticket");
    card.appendChild(el("strong", null,
      `${t.ticket_id} — ${t.subject} [${t.status}] submitted by ${t.submitted_by}`));
    card.appendChild(el("pre", null, t.employee_description));
    if (t.status === "resolved") {
      card.appendChild(el("div", "meta",
        `Published as document ${t.document_id} (+${t.chunks_added} chunks)`));
      card.appendChild(el("pre", null, t.technician_resolution));
    } else if ($("role").value === "technician") {
      const box = el("textarea");
      box.rows = 3;
      box.placeholder = "Technician resolution…";
      const payload = payloads.find((p) => t.subject.includes(p.document_id));
      if (payload) box.value = payload.technician_resolution;
      const go = el("button", null, "Resolve and publish");
      go.addEventListener("click", async () => {
        go.disabled = true;
        try {
          const res = await post(`/api/tickets/${t.ticket_id}/resolve`,
                                 { resolution: box.value });
          renderStatus(res.corpus);
          await loadTickets();
        } catch (err) {
          card.appendChild(el("div", "banner danger", err.message));
          go.disabled = false;
        }
      });
      card.appendChild(box);
      card.appendChild(go);
    } else {
      card.appendChild(el("div", "meta", "Switch Role to Technician to resolve this ticket."));
    }
    list.appendChild(card);
  }
}

$("ticket-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const role = $("role").value;
  try {
    await post("/api/tickets", {
      subject: $("ticket-subject").value,
      description: $("ticket-description").value,
      submitted_by: role,
      membership: role === "attacker" ? "attacker" : "clean",
    });
    $("ticket-description").value = "";
    $("ticket-subject").value = "";
    $("payload-picker").value = "";
    await loadTickets();
    await refreshStatus();
  } catch (err) {
    $("ticket-list").prepend(el("div", "banner danger", err.message));
  }
});

$("role").addEventListener("change", () => {
  if (!$("panel-tickets").classList.contains("hidden")) loadTickets();
});

// --- corpus --------------------------------------------------------------

async function loadCorpus() {
  const { documents } = await api("/api/corpus");
  const table = $("corpus-table");
  table.textContent = "";
  const head = el("tr");
  for (const h of ["id", "title", "type", "membership", "chunks"]) {
    head.appendChild(el("th", null, h));
  }
  table.appendChild(head);
  for (const d of documents) {
    const row = el("tr", d.membership);
    for (const v of [d.document_id, d.title, d.source_type, d.membership, String(d.chunks)]) {
      row.appendChild(el("td", null, v));
    }
    table.appendChild(row);
  }
}

// --- reset ---------------------------------------------------------------

$("reset").addEventListener("click", async () => {
  renderStatus(await post("/api/reset"));
  $("transcript").textContent = "";
  await loadTickets();
});

refreshStatus();
loadPayloads();
$("question").focus();
