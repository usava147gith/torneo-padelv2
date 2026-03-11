// Ensure global tournament object exists (prevents "torneo is not defined")
window.torneo = window.torneo || { giocatori: [], partite: [], matches: [], tabellone: [] };

// Helper to safely read torneo even if defined later
function _getTorneo() {
  return window.torneo || { giocatori: [], partite: [], matches: [], tabellone: [] };
}

// ===============================
//  EXPORT / IMPORT FUNCTIONS FOR ANDROID + BROWSER
// ===============================

function _getPlayersArray(t) {
    if (!t) return [];
    if (Array.isArray(t.giocatori)) return t.giocatori;
    if (Array.isArray(t.players)) return t.players;
    if (Array.isArray(t.partecipanti)) return t.partecipanti;
    return [];
}

function _getMatchesArray(t) {
    if (!t) return [];
    if (Array.isArray(t.partite)) return t.partite;
    if (Array.isArray(t.matches)) return t.matches;
    if (Array.isArray(t.tabellone)) return t.tabellone;
    return [];
}

function _escapeCsvCell(value) {
    if (value === null || value === undefined) return "";
    const s = String(value);
    if (s.includes('"') || s.includes(',') || s.includes('\n')) {
        return `"${s.replace(/"/g, '""')}"`;
    }
    return s;
}

function exportTorneoJson() {
    try {
        const t = _getTorneo();
        const json = JSON.stringify(t);
        if (window.Android && typeof Android.exportJson === 'function') {
            Android.exportJson(json);
            return;
        }
        const blob = new Blob([json], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "torneo.json";
        a.click();
        URL.revokeObjectURL(url);
    } catch (e) {
        console.error("exportTorneoJson error", e);
        alert("Errore esportazione JSON: " + e.message);
    }
}

function exportTorneoCsv() {
    try {
        const t = _getTorneo();
        const players = _getPlayersArray(t);
        let csv = "Giocatore,Punteggio\n";
        players.forEach(g => {
            const nome = g.nome || g.name || g.player || "";
            const punteggio = g.punteggio || g.score || g.points || "";
            csv += `${_escapeCsvCell(nome)},${_escapeCsvCell(punteggio)}\n`;
        });

        if (window.Android && typeof Android.exportCsv === 'function') {
            Android.exportCsv(csv);
            return;
        }

        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "torneo_giocatori.csv";
        a.click();
        URL.revokeObjectURL(url);
    } catch (e) {
        console.error("exportTorneoCsv error", e);
        alert("Errore esportazione CSV: " + e.message);
    }
}

function exportTabelloneCsv() {
    try {
        const t = _getTorneo();
        const matches = _getMatchesArray(t);
        let csv = "Round,Coppia 1,Coppia 2,Punteggio\n";

        matches.forEach(p => {
            const round = p.round || p.turno || p.stage || "";
            const c1 = p.coppia1 || p.teamA || p.playerA || p.player1 || p.coupleA || p.team1 || "";
            const c2 = p.coppia2 || p.teamB || p.playerB || p.player2 || p.coupleB || p.team2 || "";
            const score = p.punteggio || p.score || p.result || "";
            csv += `${_escapeCsvCell(round)},${_escapeCsvCell(c1)},${_escapeCsvCell(c2)},${_escapeCsvCell(score)}\n`;
        });

        if (window.Android && typeof Android.exportCsv === 'function') {
            Android.exportCsv(csv);
            return;
        }

        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "tabellone.csv";
        a.click();
        URL.revokeObjectURL(url);
    } catch (e) {
        console.error("exportTabelloneCsv error", e);
        alert("Errore esportazione tabellone: " + e.message);
    }
}

function handleJsonImport(event) {
    try {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(e) {
            importaTorneo(e.target.result);
        };
        reader.readAsText(file);
    } catch (e) {
        console.error("handleJsonImport error", e);
        alert("Errore importazione file: " + e.message);
    }
}

function importaTorneo(jsonString) {
    try {
        const parsed = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;
        window.torneo = parsed;
        if (typeof aggiornaUI === 'function') {
            aggiornaUI();
        } else {
            console.warn("aggiornaUI() non trovata: aggiorna manualmente la UI");
        }
    } catch (e) {
        console.error("importaTorneo error", e);
        alert("Errore parsing JSON: " + e.message);
    }
}

