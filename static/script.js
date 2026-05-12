
async function shortenUrl() {
const input = document.getElementById("urlInput");
const btn   = document.getElementById("shortenBtn");
const err   = document.getElementById("errorMsg");
const box   = document.getElementById("resultBox");
const link  = document.getElementById("resultLink");

const url = input.value.trim();
err.classList.remove("visible");
box.classList.remove("visible");

if (!url) {
    err.textContent = "// please enter a URL first";
    err.classList.add("visible");
    return;
}

btn.disabled = true;
btn.textContent = "...";

try {
    const res  = await fetch("/api/shorten", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
    });
    const data = await res.json();

    if (!res.ok) {
    err.textContent = "// " + (data.error || "Something went wrong.");
    err.classList.add("visible");
    } else {
    link.href        = data.short_url;
    link.textContent = data.short_url;
    box.classList.add("visible");
    document.getElementById("copyBtn").textContent = "copy";
    document.getElementById("copyBtn").classList.remove("copied");
    loadLinks();
    }
} catch {
    err.textContent = "// network error. is the server running?";
    err.classList.add("visible");
} finally {
    btn.disabled = false;
    btn.textContent = "Snip it";
}
}

async function copyLink() {
const url = document.getElementById("resultLink").textContent;
await navigator.clipboard.writeText(url);
const btn = document.getElementById("copyBtn");
btn.textContent = "copied!";
btn.classList.add("copied");
setTimeout(() => {
    btn.textContent = "copy";
    btn.classList.remove("copied");
}, 2000);
}

async function loadLinks() {
const res   = await fetch("/api/links");
const links = await res.json();
const tbody = document.getElementById("linksBody");

if (!links.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="4">No links yet. Snip one above!</td></tr>`;
    return;
}

tbody.innerHTML = links.map(l => `
    <tr>
    <td><span class="original-url" title="${l.original}">${l.original}</span></td>
    <td><a class="short-link" href="${BASE}/${l.short_code}" target="_blank">${l.short_code}</a></td>
    <td><span class="clicks-badge">${l.clicks}</span></td>
    <td><button class="del-btn" onclick="deleteLink('${l.short_code}')">del</button></td>
    </tr>
`).join("");
}

async function deleteLink(code) {
await fetch(`/api/links/${code}`, { method: "DELETE" });
loadLinks();
}

document.getElementById("urlInput").addEventListener("keydown", e => {
if (e.key === "Enter") shortenUrl();
});

loadLinks();