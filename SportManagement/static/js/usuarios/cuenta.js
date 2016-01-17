function submit_usuarios_cuenta(){
    var guardar = true;
    $("#error_email").hide();
    $("#error_pass").hide();
    $(".obligatorio").each(function(){
        if($(this).val() == "" || $(this).val() == 0){
            guardar = false;
            $(this).parent().parent().addClass("has-error");
        }
        else{
            $(this).parent().parent().removeClass("has-error").addClass("has-success");
        }
    });
    if(guardar == true){
        if($("#password1").val() == $("#password2").val()){
            if(isValidEmailAddress($("#email").val())){
                guardar = true;
            }
            else{
                $("#error_email").show();
                $("#email").parent().parent().removeClass("has-success").addClass("has-error");
                guardar = false;
            }
        }else{
            $("#error_pass").show();
            $("#password1").parent().parent().addClass("has-error");
            $("#password2").parent().parent().addClass("has-error");
            guardar = false;
        }
    }
    if(guardar == true){
        $("#formulario_cuenta").submit();
    }
}

function isValidEmailAddress(emailAddress) {
    var pattern = new RegExp(/^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i);
    return pattern.test(emailAddress);
}

function actualiza_deportes(elem){
    var club_id = $(elem).val();
    $.ajax({
        data: {'club_id':club_id},
        url: '/clubes_niveles_cuenta',
        type: 'GET',
        success: function(data){
          var html;
          //Eliminamos opciones anteriores:
          if(document.getElementById("id_deporte").options.length != 0){
              document.getElementById("id_deporte").options.length = 0;
          }

          //Añadimos nuevos valores
          $("#id_deporte").append("<option value=\"0\">Seleccione un deporte...</option>");
          for(var i = 0; i < data.length; i++){
            var s = '<option value="'+data[i].pk+'">'+data[i].fields.deporte+'</option>';
            $("#id_deporte").append(s);
          }
          $("#id_deporte").attr("disabled", false);
          $("#id_nivel").attr("disabled", true);
        }
    });
}

function actualiza_niveles(elem){
    var deporte_id = $(elem).val();
    var club_id = $("#id_club").val();
    $.ajax({
        data: {'deporte_id':deporte_id, 'club_id':club_id},
        url: '/clubes_deportes_cuenta',
        type: 'GET',
        success: function(data){
          var html;
          //Eliminamos opciones anteriores:
          if(document.getElementById("id_nivel").options.length != 0){
              document.getElementById("id_nivel").options.length = 0;
          }

          //Añadimos nuevos valores
          $("#id_nivel").append("<option value=\"0\">Seleccione un nivel...</option>");
          for(var i = 0; i < data.length; i++){
            var s = '<option value="'+data[i].pk+'">'+data[i].fields.nivel+'</option>';
            $("#id_nivel").append(s);
          }
          $("#id_nivel").attr("disabled", false);
        }
    });
}

function submit_agregar_deportes(){
    var tiene_errores = false;
    $(".obligatorio_deportes").each(function(){
        if($(this).val() == 0){
            $(this).parent().parent().addClass('has-error');
            $(this).parent().parent().removeClass('has-success');
            tiene_errores = true;
        }
        else{
            $(this).parent().parent().removeClass('has-error');
            $(this).parent().parent().addClass('has-success');
        }
    });

    if(!tiene_errores){
        $("#form_deportes").submit();
    }
}

function eliminar_nivel(nivel_id){
    var form = $("#form_niveles_"+nivel_id).serialize();
    $.ajax({
        data: form,
        url: '/eliminar_niveles_club_cuenta',
        type: 'POST',
        success: function(data){
            var r = JSON.parse(data);
            if(r.error == "" || r.error == null){
                $("#nivel_"+nivel_id).hide("slide", {direction: "up" }, "slow");
                $("#nivel_"+nivel_id).remove();
                $("#form_niveles_"+nivel_id).remove();
                if($("#menu_niveles_deportes").children().length == 1){
                    $("#menu_niveles_deportes").html("<li>No ha seleccionado ningún nivel</li>");
                }
            }
            else{
                $("#errores_ajax").html(r.error);
                $("#errores_ajax").parent().parent().show("slide", {direction: "down" }, "slow");;
            }
        }
    });
}