// ===============================
//  EXPORT / IMPORT FUNCTIONS FOR ANDROID + BROWSER
//  Paste this at the end of script.js
// ===============================

/**
 * Utility: safe getter for players array (handles different naming)
 */
function _getPlayersArray(torneo) {
    if (!torneo) return [];
    if (Array.isArray(torneo.giocatori)) return torneo.giocatori;
    if (Array.isArray(torneo.players)) return torneo.players;
    if (Array.isArray(torneo.partecipanti)) return torneo.partecipanti;
    return [];
}

/**
 * Utility: safe getter for matches/tabellone array
 */
function _getMatchesArray(torneo) {
    if (!torneo) return [];
    if (Array.isArray(torneo.partite)) return torneo.partite;
    if (Array.isArray(torneo.matches)) return torneo.matches;
    if (Array.isArray(torneo.tabellone)) return torneo.tabellone;
    return [];
}

/**
 * EXPORT JSON
 */
function exportTorneoJson() {
    try {
        const json = JSON.stringify(torneo);
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

/**
 * EXPORT CSV (giocatori e punteggi)
 */
function exportTorneoCsv() {
    try {
        const players = _getPlayersArray(torneo);
        let csv = "Giocatore,Punteggio\n";
        players.forEach(g => {
            const nome = g.nome || g.name || g.player || "";
            const punteggio = g.punteggio || g.score || g.points || "";
            csv += `${nome},${punteggio}\n`;
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

/**
 * EXPORT TABELLONE COMPLETO
 * Adatta automaticamente a campi comuni: round, coppia1/coppia2, teamA/teamB, punteggio/score
 */
function exportTabelloneCsv() {
    try {
        const matches = _getMatchesArray(torneo);
        let csv = "Round,Coppia 1,Coppia 2,Punteggio\n";

        matches.forEach(p => {
            const round = p.round || p.turno || p.stage || "";
            const c1 = p.coppia1 || p.teamA || p.playerA || p.player1 || p.coupleA || "";
            const c2 = p.coppia2 || p.teamB || p.playerB || p.player2 || p.coupleB || "";
            const score = p.punteggio || p.score || p.result || "";
            csv += `${round},${c1},${c2},${score}\n`;
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

/**
 * HANDLE FILE INPUT IMPORT (browser)
 */
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

/**
 * IMPORT JSON into page data and refresh UI
 */
function importaTorneo(jsonString) {
    try {
        const parsed = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;
        // Replace tournament data
        torneo = parsed;
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
