function loginDialog(){
    $("#div_login").show();
    $("#div_login").dialog({
		modal: true,
		height: "auto",
        width: "35%",
        title: "Acceder"
    });
}

function submit_login(){
    var form = $("#form_login").serialize();
    var username = $("#id_username").val();
    var pass = $("#id_password").val();
    $.ajax({
        url: '/login',
        data: form,
        type: 'POST',
        success: function(request){
            var r = JSON.parse(request);
            if(r.error == ""){
                if(r.id != "" && r.rol_id == 1){
                    window.location.href = '/administrador/'+r.id;
                }
                else if(r.id != "" && r.rol_id != 1){
                    window.location.href = '/usuario/'+r.id;
                }
            }
            else{
                $("#form_error").html(r.error);
                $("#div_form_error").slideDown();
            }
        }
    });
}

function registroDialog(){
    $("#div_registro").show();
    $("#div_registro").dialog({
		modal: true,
		height: "auto",
        width: "35%",
        title: "Registro"
    });
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
        $.ajax({
            url: '/registro',
            data: form,
            type: 'POST',
            success: function(request){
                var r = JSON.parse(request);
                if(r.error == ""){
                    if(r.id != ""){
                        window.location.href = '/profile?id='+r.id;
                    }
                }
                else{
                    $("#form_error").html(r.error);
                    $("#div_form_error").slideDown();
                }
            }
        });
    }
    else{
        $("#form_registro_error").html(error_texto);
        $("#div_form_registro_error").slideDown();
    }
}