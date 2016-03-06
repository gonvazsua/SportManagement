function actualiza_municipios(elem){
    var provincia_id = $(elem).val();
    $("#id_municipio").attr("disabled", false);
    $.ajax({
        data: {'provincia_id':provincia_id},
        url: '/municipios_ajax',
        type: 'GET',
        success: function(data){
          var html;
          //Eliminamos opciones anteriores:
          if(document.getElementById("id_municipio").options.length != 0){
              document.getElementById("id_municipio").options.length = 0;
          }

          //Añadimos nuevos valores
          $("#id_municipio").append("<option value=\"0\">Seleccione municipio</option>");
          for(var i = 0; i < data.length; i++){
            var s = '<option value="'+data[i].pk+'">'+data[i].fields.municipio+'</option>';
            $("#id_municipio").append(s);
          }
        }
    });
}

function submit_completar_registro(){
    if($("#telefono").val() != "" || $("#id_municipio").val() != 0){
        $("#icono_completar_registro").removeClass("fa-save");
        $("#icono_completar_registro").addClass("fa-spinner");
        var form = $("#form_completar_registro").serialize();
        $.ajax({
            data: form,
            url: '/completar_datos_inicio',
            type: 'POST',
            success: function(data){
                var r = JSON.parse(data);
                if(r.error == ""){
                    cerrar_dialogo_informacion();
                }
            }
        });
    }
}

function cerrar_dialogo_informacion(){
    $("#panel_completar_registro").hide("slide", {direction: "up" }, "slow");
    $("#panel_completar_registro").remove();
    $(".ui-effects-wrapper").remove();
}

function mostrar_capa_abajo(id){
    $("#"+id).show("slide", {direction: "up" }, "slow");
}

function marcar_como_leida(notif_id){
    $.ajax({
        data: {'notificacion_id':notif_id},
        url: '/marcar_leida',
        type: 'GET',
        success: function(data){
            var r = JSON.parse(data);
            if(r.error == ""){
                $("#btn_aceptar_notif_pag_principal_"+notif_id).attr("disabled", true);
                $("#btn_aceptar_notif_pag_principal_"+notif_id).removeClass("hover-success");
                $("#btn_aceptar_notif_pag_principal_"+notif_id).removeClass("btn-default");
                $("#btn_aceptar_notif_pag_principal_"+notif_id).addClass("btn-success");
                $("#icono_notificacion_"+notif_id).removeClass("fa-check");
                $("#icono_notificacion_"+notif_id).addClass("fa-thumbs-o-up");
            }
        }
    });
}