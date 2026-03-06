// ===============================
//  EXPORT JSON PER ANDROID
// ===============================
function exportTorneoJson() {
    const json = JSON.stringify(torneo);
    Android.exportJson(json);
}

// ===============================
//  EXPORT CSV PER ANDROID
// ===============================
function exportTorneoCsv() {
    let csv = "Giocatore,Punteggio\n";
    torneo.giocatori.forEach(g => {
        csv += `${g.nome},${g.punteggio}\n`;
    });
    Android.exportCsv(csv);
}

// ===============================
//  IMPORT JSON DA ANDROID
// ===============================
function importaTorneo(jsonString) {
    torneo = JSON.parse(jsonString);
    aggiornaUI();
}
