function buscar_clubes(){
    var provincia_id = $("#provincia_id").val();
    var municipio_id = $("#id_municipio").val();
    if(provincia_id != 0 || municipio_id != 0){
        $("#form_buscador_clubes").submit();
    }
}

function inscripcion_clubes(club_id){
    var form = $("#form_inscripcion_club_"+club_id).serialize();
    $.ajax({
        data: form,
        url: '/buscador/clubes/inscripcion',
        type: 'POST',
        success: function(data){
            var r = JSON.parse(data);
            if(r.error == ""){
                $("#btn_inscripcion_"+club_id).removeClass("btn-info");
                $("#btn_inscripcion_"+club_id).addClass("btn-success");
                var html = '<i class="fa fa-check"></i> Petición enviada';
                $("#btn_inscripcion_"+club_id).html(html);
                $("#btn_inscripcion_"+club_id).attr("disabled","disabled")
            }
            else{
                $("#error_inscripcion_club_"+club_id).html(r.error);
                $("#error_inscripcion_club_"+club_id).show();
            }
        }
    });
}

function baja_clubes(club_id){
    var form = $("#form_baja_club_"+club_id).serialize();
    $.ajax({
        data: form,
        url: '/buscador/clubes/baja',
        type: 'POST',
        success: function(data){
            var r = JSON.parse(data);
            if(r.error == ""){
                $("#fila_club_"+club_id).hide("slide", {direction: "up" }, "slow");
                $("#ok_baja_club_"+club_id).show("slide", {direction: "down" }, "slow");
            }
            else{
                $("#error_baja_club_"+club_id).html(r.error);
                $("#error_baja_club_"+club_id).show();
            }
        }
    });
}