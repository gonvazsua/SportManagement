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
                        action = '/usuario/'+r.id;
                        $("#form_redirige").attr("action", action);
                        $("#form_redirige").submit();
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