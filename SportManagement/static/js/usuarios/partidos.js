function inscripcion_partido(){
    var form = $("#peticion_partido").serialize();
    $.ajax({
        data: form,
        url: '/inscripcion_partidos',
        type: 'POST',
        success: function(data){
            var r = JSON.parse(data);
            if(r.error == ""){
                $("#btn_inscripcion").removeClass("btn-info");
                $("#btn_inscripcion").addClass("btn-success");
                var html = '<i class="fa fa-check"></i> Petición enviada';
                $("#btn_inscripcion").html(html);
                $("#btn_inscripcion").attr("disabled","disabled")
            }
            else{
                $("#error_inscripcion").html(r.error);
                $("#error_inscripcion").parent().parent().show("slide", {direction: "down" }, "slow");
            }
        }
    });
}

function actualizar_franja_hora(elem){
    var club_id = $(elem).val();
    $.ajax({
        data: {'club_id':club_id},
        url: '/actualizar_franjas_club_ajax',
        type: 'GET',
        success: function(data){
          var html;
          //Eliminamos opciones anteriores:
          if(document.getElementById("id_hora").options.length != 0){
              document.getElementById("id_hora").options.length = 0;
          }

          //Añadimos nuevos valores
          $("#id_hora").append("<option value=\"0\">Seleccione hora...</option>");
          for(var i = 0; i < data.length; i++){
            var s = '<option value="'+data[i].pk+'">'+data[i].fields.inicio+' - '+data[i].fields.fin+'</option>';
            $("#id_hora").append(s);
          }
          $("#id_hora").attr("disabled", false);
        }
    });
}

function inicia_pagina_buscador_partidos(){
    $.datepicker.regional['es'] = {
         closeText: 'Cerrar',
         prevText: '<Ant',
         nextText: 'Sig>',
         currentText: 'Hoy',
         monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
         monthNamesShort: ['Ene','Feb','Mar','Abr', 'May','Jun','Jul','Ago','Sep', 'Oct','Nov','Dic'],
         dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
         dayNamesShort: ['Dom','Lun','Mar','Mié','Juv','Vie','Sáb'],
         dayNamesMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sá'],
         weekHeader: 'Sm',
         dateFormat: 'dd/mm/yy',
         firstDay: 1,
         isRTL: false,
         showMonthAfterYear: false,
         yearSuffix: ''
         };
         $.datepicker.setDefaults($.datepicker.regional['es']
    );

    $("#id_fecha").datepicker({
        dateFormat: 'dd/mm/yy'
    });
}