$(document).ready(function () {
    function updateGraph() {
        //let choix = $("#filtre").val();       // Récupérer le choix (Sexe/Filière)
        //let annee = $("#annee_select").val();  Récupérer l'année sélectionnée
        let classe = $("#select_classe").val();       // Récupérer la classe

        $.ajax({
            url: "/update_graph",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ classe: classe }), // Envoyer les 2 filtres
            success: function (response) {
            console.log("Données reçues :", response);

            // Mise à jour des compteurs
            $("#total_students").text(response.total);
            $("#classe_students").text(response.total_classe);
            $("#homme_students").text(response.total_homme);
            $("#femme_students").text(response.total_femme);

            // ----------------------
            //  🔵 Mise à jour du tableau df_evals
            // ----------------------
            let tbody = $("#table_evals tbody");
            tbody.empty();

            response.evaluations.forEach(row => {
                tbody.append(`
                    <tr>
                        <td>${row["Nom&Prenoms"]}</td>
                        <td>${row.nb_evaluations}</td>
                    </tr>
                `);
            });
            },
            error: function (xhr, status, error) {
                console.error("Erreur AJAX :", xhr.responseText);  // 🚨 Affichage en cas d'erreur
            }
        });
    }

    // Exécuter quand on change un des filtres
    $("#select_classe").change(updateGraph);

    // Charger un premier graphique au chargement de la page
    updateGraph();
});
