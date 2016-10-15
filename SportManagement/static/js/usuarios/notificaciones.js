function marcar_como_leida(notif_id){
    $.ajax({
        data: {'notificacion_id':notif_id},
        url: '/marcar_leida',
        type: 'GET',
        success: function(data){
            var r = JSON.parse(data);
            if(r.error == ""){
                $("#panel_"+notif_id).removeClass("fondo-info");
                $("#texto_leida_"+notif_id).hide();
                $("#texto_leida_"+notif_id).remove();
            }
        }
    });
}