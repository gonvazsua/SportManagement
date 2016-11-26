/*Desplazamiento animado, del origen ELEM al DESTINO*/
function desplaza(destino){
	$('html,body').animate({
    	scrollTop: $('#'+destino).offset().top
	}, 2000);
}

function loginDialog(){
    $('#login_modal').modal('show')
}

function submit_login(){
    var form = $("#form_login").serialize();
    var username = $("#id_usuario").val();
    var pass = $("#id_password").val();
    if(username != "" && pass != ""){
        $("#icono_login").addClass("glyphicon-time");
        $.ajax({
            url: '/login',
            data: form,
            type: 'POST',
            success: function(request){
                var r = JSON.parse(request);
                if(r.error == ""){
                    if(r.id != "" && r.rol_id == 1){
                        action = '/administrador/'+r.id;
                        $("#form_redirige").attr("action", action);
                        $("#form_redirige").submit();
                    }
                    else if(r.id != "" && r.rol_id == 2){
                        action = '/usuario/'+r.id;
                        $("#form_redirige").attr("action", action);
                        $("#form_redirige").submit();
                    }
                }
                else{
                    $("#form_error").html(r.error);
                    $("#form_error").slideDown();
                    $("#icono_login").removeClass("glyphicon-time");
                }
            }
        });
    }
    else{
        $("#form_error").html("Rellene correctamente todos los campos");
        $("#form_error").slideDown();
    }
}

function submit_registro(){
    $("#form_registro_error").parent().parent().hide()
    var form = $("#form_registro").serialize();
    var error = false;
    var error_texto = "";
    var regex_email = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    if ($("#id_nombre").val() == "" || $("#id_apellidos").val() == "" || $("#id_username").val() == "" || $("#id_email").val() == "" ||
        $("#id_password1").val() == "" || $("#id_password2").val() == ""){
        error = true;
        error_texto = "Debe rellenar todos los campos";
    }
    else if(!regex_email.test($("#id_email").val())){
        error = true;
        error_texto = "Formato de email incorrecto";
    }
    else if($("#id_password1").val() != $("#id_password2").val()){
        error = true;
        error_texto = "Las contraseñas no coinciden";
    }
    if(!error){
        $("#icono_registro").removeClass("glyphicon-user");
        $("#icono_registro").addClass("glyphicon-time");
        $.ajax({
            url: '/registro',
            data: form,
            type: 'POST',
            success: function(request){
                var r = JSON.parse(request);
                if(r.error == ""){
                    if(r.id != ""){
                        $("#form_registro_error").removeClass("bg-danger");
                        $("#form_registro_error").addClass("bg-success");
                        $("#form_registro_error").html("Se ha registrado con éxito, ya puedes acceder a tu cuenta");
                        $("#form_registro_error").parent().parent().show();
                    }
                }
                else{
                    $("#form_registro_error").html(r.error);
                    $("#div_form_registro_error").slideDown();
                    $("#icono_registro").removeClass("glyphicon-time");
                    $("#icono_registro").addClass("glyphicon-user");
                }
            }
        });
    }
    else{
        $("#form_registro_error").html(error_texto);
        $("#div_form_registro_error").slideDown();
    }
}

function validar_email(){
    var subject = $("#subject").val();
    var from_email = $("#from_email").val();
    var message = $("#message").val();
    if(subject != "" && from_email != "" && message != ""){
        enviar_email(subject, from_email, message);
    }
    else{
        $("#error_email .alert").html("Rellene todos los campos correctamente.");
        $("#error_email").show();
    }
}

function enviar_email(subject, from_email, message){
    var form = $("#form_contacto").serialize();
    $.ajax({
        url: '/enviarEmail',
        data: form,
        type: 'POST',
        success: function(request){
            var r = JSON.parse(request);
            if(r.error == ""){
                $("#error_email .alert").removeClass("alert-danger").addClass("alert-success");
                $("#error_email .alert").html("Su consulta se ha enviado correctamente.")
                $("#error_email").show();
            }
            else{
                $("#error_email .alert").html(r.error);
                $("#error_email").show();
            }
        }
    });
}

function submit_intro(){
    $("#id_password").keypress(function(e){
        if(e.which == 13) {
            submit_login();
        }
    });
}

function pass_olvidada(){
    $("#login_modal").modal("hide");
    $('#login_modal_pass').modal('show')
}

function submit_olvida_pass(){

    $("#btn-pass").attr("disabled", true);

    if($("#email_pass").val() != ""){
        $("#email_pass").parent().removeClass("has-error");
        $("#alert_pass").html("Estamos cambiando tu contraseña...");
        form = $("#form_password").serialize();
        $.ajax({
            url: '/recuperar_pass',
            data: form,
            type: 'POST',
            success: function(request){
                var r = JSON.parse(request);
                if(r.error == ""){
                    $("#alert_pass").removeClass("alert-info").addClass("alert-success");
                    $("#alert_pass").html("Se ha enviado al email tu nueva contraseña");
                    $("#alert_pass").delay(10000).html("Te enviaremos un email con tu nueva contraseña");
                }
                else{
                    $("#alert_pass").removeClass("alert-success").addClass("alert-danger");
                    $("#alert_pass").html(r.error);
                }
            }
        });
    }
    else{
        $("#email_pass").parent().addClass("has-error");
    }

    $("#btn-pass").attr("disabled", false);
}

function ir_registro_desde_login(){

    //Cerrar modal login
    $("#login_modal").modal("hide");
    desplaza("apartado_registro");
}

function addHtml(inout){
    var html = "<i class='fa fa-thumbs-up fa-fw'></i>";

    if(inout == 'in'){
        html += " Síguenos en Facebook"
    }

    $("#btn-facebook").html(html);

}

/******************************
    Buscador de clubes
******************************/
function actualiza_municipios(elem){
    var provincia_id = $(elem).val();

    if(provincia_id != 0){
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
              $("#id_municipio").append("<option value=\"0\">Selecciona municipio</option>");
              for(var i = 0; i < data.length; i++){
                var s = '<option value="'+data[i].pk+'">'+data[i].fields.municipio+'</option>';
                $("#id_municipio").append(s);
              }

              $("#id_municipio").attr("disabled", false);
            }
        });
    }
    else{
        $("#id_municipio").html("<option value='0'>Selecciona provincia</option>");
        $("#id_municipio").attr("disabled", true);
    }
}

function buscar_club_inicio(){

    var provincia_id = $("#provincia_id").val();
    $("#provincia_id").parent().removeClass("has-error");

    if (provincia_id != 0 && provincia_id != ""){
        $("#buscador_clubes").submit();
    }
    else{
        $("#provincia_id").parent().addClass("has-error");
    }
}

function buscar_club_ajax(){

    $.ajax({
        data: $("#form-buscar").serialize(),
        url: $("#form-buscar").attr("action"),
        type: 'POST',
        success: function(data){

            $("#primeros-resultados").slideUp("slow");
            $("#primeros-resultados").remove();
            $("#resultados_buscador").html(data);
            $("#resultados_buscador").slideDown("slow");
        }
    });

}

function inicializar_datepicker(){
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

function buscar_partidos_ajax(){
    $.ajax({
        data: $("#buscador-partidos").serialize(),
        url: $("#buscador-partidos").attr("action"),
        type: 'POST',
        success: function(data){

            $("#resultados_buscador").html(data);
            $("#resultados_buscador").slideDown("slow");
        }
    });
}

function mostrar_ocultar_club(menu){

    if(menu == 'eventos'){

        $("#enlace_club_partidos").removeClass("active");
        $("#enlace_club_eventos").addClass("active");

        $("#apartado_club_partidos").slideUp( "slow", function() {
            $("#apartado_club_eventos").slideDown("slow");
        });

    }
    else{

        $("#enlace_club_eventos").removeClass("active");
        $("#enlace_club_partidos").addClass("active");

        $("#apartado_club_eventos").slideUp( "slow", function() {
            $("#apartado_club_partidos").slideDown("slow");
        });

    }

}