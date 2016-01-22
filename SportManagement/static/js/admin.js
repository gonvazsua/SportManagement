

$(document).ready(function() {

    /*
    $('#dataTables-jugadores-busqueda').DataTable({
        responsive: true,
        "language":{
            "sProcessing":     "Procesando...",
            "sLengthMenu":     "Mostrar _MENU_ registros",
            "sZeroRecords":    "No se encontraron resultados",
            "sEmptyTable":     "Ningún dato disponible en esta tabla",
            "sInfo":           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "sInfoEmpty":      "Mostrando registros del 0 al 0 de un total de 0 registros",
            "sInfoFiltered":   "(filtrado de un total de _MAX_ registros)",
            "sInfoPostFix":    "",
            "sSearch":         "Buscar:",
            "sUrl":            "",
            "sInfoThousands":  ",",
            "sLoadingRecords": "Cargando...",
            "oPaginate": {
                "sFirst":    "Primero",
                "sLast":     "Último",
                "sNext":     "Siguiente",
                "sPrevious": "Anterior"
            },
            "oAria": {
                "sSortAscending":  ": Activar para ordenar la columna de manera ascendente",
                "sSortDescending": ": Activar para ordenar la columna de manera descendente"
            }
        }
    });

    */

    actualiza_enlace_menu();
    inicia_pagina_nuevo_partido();
    //inicia_pagina_estadisticas();

});

function mostrar(id){
    $(id).show();
}

function mostrar_efecto(id){
    $(id).show("slide", {direction: "down" }, "slow");
}

function ocultar(id){
    $(id).hide();
}

function ocultar_efecto(id){
    $(id).hide("slide", {direction: "up" }, "slow");
}

function actualiza_enlace_menu(){
    $("#side-menu").find("a").each(function(index){
        $(this).removeClass("active");
    });
}

/******************************************************************************/
/* Página de nuevo partido */
/******************************************************************************/

function inicia_pagina_nuevo_partido(){
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

function comprobar_disponibilidad_partido(isAjax){
    if($("#id_fecha").val() == "" || $("#id_hora").val() == 0 || $("#id_pista").val() == 0){
        $("#error_campos_partido").show();
    }
    else{
        $("#error_campos_partido").hide();

        if(esFechaMenorActual($("#id_fecha").val())){
            //Comprobar que no es anterior a hoy
            $("#error_fecha_disponibilidad").show();
        }else{
            $("#error_campos_partido").hide();
            $("#icono_comprobar_disponibilidad").show();
            if( !isAjax ){
                $("#form_crear_partido_fecha_hora").submit();
            }
            else{
                $.ajax({
                    data: $("#form_crear_partido_fecha_hora").serialize(),
                    url: '/comprueba_disponibilidad_partido_ajax',
                    type: 'POST',
                    success: function(request){
                        var r = JSON.parse(request);
                        if(r.disponible == true){
                            $("#icono_comprobar_disponibilidad").hide();
                            $("#icono_pista_no_disponible").hide();
                            $("#icono_pista_disponible").show();
                            $("#btn_disponibilidad").removeClass("btn-primary").removeClass("btn-danger").addClass("btn-success");
                            $("#error_pista").hide();
                            $("#row_partido").show();
                        }
                        else{
                            $("#icono_comprobar_disponibilidad").hide();
                            $("#icono_pista_disponible").hide();
                            $("#icono_pista_no_disponible").show();
                            $("#btn_disponibilidad").removeClass("btn-primary").removeClass("btn-success").addClass("btn-danger");
                            $("#error_pista").show();
                        }
                    }
                });
            }
        }
    }
}

function filtrar_niveles_jugadores(){
    nivel_seleccionado = $("#nivel_filtro").val();
    if(nivel_seleccionado == 0){
        //Se ha seleccionado mostrar todos menos seleccionados
        $(".nivel").each(function(){
            if(!$(this).parent().parent().hasClass("seleccionado")){
                $(this).parent().parent().show();
            }
        });
    }
    else{
        $(".nivel").each(function(){
            if($(this).val() == nivel_seleccionado && !$(this).parent().parent().hasClass("seleccionado")){
                $(this).parent().parent().show();
            }
            else{
                $(this).parent().parent().hide();
            }
        });
    }
}

function filtrar_palabra_clave(){
    $("#nivel_filtro").val(0);
    filtrar_niveles_jugadores();

    var palabra_clave = $("#palabra_clave").val();
    var ya_mostrado = false;
    var contador_tds = 0;

    if(palabra_clave != ""){
        $(".campo_busqueda").each(function(){

            var texto_td = $(this).html();

            //Actualizamos valor contador, si es >3 significa que vamos a una fila nueva y se reinicia su valor.
            contador_tds = contador_tds > 3 ? 1 : contador_tds + 1;
            if(contador_tds == 1) ya_mostrado = false;

            //Nos saltamos los tds que tienen el texto vacio
            // y los elementos que tienen hijos ocultos, es decir,
            // los que son elementos para seleccionar y el campo Nivel

            if(texto_td != "" && $(this).children().length == 0){
                var td_formateado = texto_td.toLowerCase();
                var pc_formateado = palabra_clave.toLowerCase();

                //Para que no se compruebe varias veces el mismo TR
                if(td_formateado.indexOf(pc_formateado) != -1 && !$(this).parent().parent().hasClass("seleccionado")){
                    $(this).parent().show();
                    ya_mostrado = true;
                }
                else{
                    if(contador_tds == 3){
                        if(!ya_mostrado)
                            $(this).parent().hide();
                        contador_tds = 0;
                    }
                }
            }
        });
    }
    else{
        filtrar_niveles_jugadores();
    }
}

function incluir_jugador(perfil_id, nombre, username, telefono){
    var max_jugadores = $("#max_jugadores").val();
    //Calculamos número de jugadores seleccionados
    var num_jugadores_seleccionados = $(".seleccionado").length;
    if(num_jugadores_seleccionados < max_jugadores){
        //Buscar fila TR disponible en la tabla de seleccionados y modificamos sus valores
        $(".vacio:first").attr("id", "jugador_partido_"+perfil_id);
        $(".vacio:first .perfil_id").val(perfil_id);
        $(".vacio:first .nombre").html(nombre);
        $(".vacio:first .username").html(username);
        $(".vacio:first .telefono").html(telefono);
        //Cambiar icono
        $(".vacio:first .fa")
            .removeClass("fa-futbol-o")
            .addClass("fa-times");

        $(".vacio:first .fa")
            .css({"cursor": "pointer"})
            .attr("title", "Eliminar jugador")
            .attr("onclick", "elimina_jugador_partido("+perfil_id+")");

        //Añadir clase success (fondo verde)
        $(".vacio:first").removeClass("warning").addClass("success");
        $(".vacio:first").removeClass("vacio");

        //Ocultar jugador de la tabla de jugadores disponibles
        $("#fila_"+perfil_id).addClass("success");
        $("#fila_"+perfil_id).slideUp("slow");
        $("#fila_"+perfil_id).addClass("seleccionado");
        $("#fila_"+perfil_id).hide();
    }
}

function elimina_jugador_partido(perfil_id){
    //Vaciar el contenido de los TD
    $("#jugador_partido_"+perfil_id+" .nombre").html("");
    $("#jugador_partido_"+perfil_id+" .username").html("");
    $("#jugador_partido_"+perfil_id+" .telefono").html("");
    $("#jugador_partido_"+perfil_id+" .perfil_id").val("");

    //Cambiar icono
    $("#jugador_partido_"+perfil_id+" .fa")
        .removeClass("fa-times")
        .addClass("fa-futbol-o")
        .attr("title", "")
        .attr("onclick", "")
        .css({"cursor":"default"});

    //Añadir clase vacío y succes cambiarlo por warning
    $("#jugador_partido_"+perfil_id)
        .addClass("vacio")
        .removeClass("success")
        .addClass("warning");

    //Volver a mostrar jugador en la tabla de jugadores
    $("#fila_"+perfil_id)
        .removeClass("seleccionado")
        .removeClass("success");

    //Solo se muestra en caso de que el nivel seleccionado sea "todos" o coincida con el que tiene el jugador
    if($("#nivel_filtro").val() == 0 || $("#fila_"+perfil_id+" .nivel").val() == $("#nivel_filtro").val()){
        $("#fila_"+perfil_id).slideDown("slow")
    }
}

function reiniciar_jugadores_nuevo_partido(){
    $(".nombre").html("");
    $(".username").html("");
    $(".telefono").html("");
    $("#tabla_jugadores_partido .perfil_id").val("");
    $("#tabla_jugadores_partido .fa-times").attr("onclick", "");
    $("#tabla_jugadores_partido .fa-times").removeClass("fa-times").addClass("fa-futbol-o");
    $("#tabla_jugadores_partido tr:not(:first)").removeClass("success").addClass("warning").addClass("vacio");
    //Solo mostrar los que coincidan con el filtro de nivel
    $(".seleccionado .nivel").each(function(){
        if($("#nivel_filtro").val() == 0 || $(this).val() == $("#nivel_filtro").val()){
            $(this).parent().parent().show();
        }
    });
    $(".seleccionado").removeClass("success").removeClass("seleccionado");
}

function actualiza_form_partido(elemento_id){
    $("#" + elemento_id + "_form").val($("#"+elemento_id).val());
}

function submit_nuevo_partido(url_guardar){
    var guardar = true;
    /*Comprobamos si no se han rellenado todos los jugadores*/
    if($(".vacio").length > 0){
        $("#botonera_form_nuevo_partido").hide("slide", {direction: "up" }, "slow");
        $("#advertencia_nuevo_partido").show("slide", {direction: "down" }, "slow");
    }
    else{
        guardar_partido(url_guardar);
    }
}

function guardar_partido(url_guardar){
    var user_id = $("#id_usuario_form").val();
    $.ajax({
        data: $("#form_partido_nuevo").serialize(),
        url: '/'+url_guardar,
        type: 'POST',
        success: function(request){
            var r = JSON.parse(request);
            if(r.error == "OK"){
                //$("#btn-submit-partido").hide();
                $("#form_partido_nuevo").hide("slide", {direction: "up" }, "slow");
                $("#advertencia_nuevo_partido").hide("slide", {direction: "up" }, "slow");
                $("#error_nuevo_partido").hide("slide", {direction: "up" }, "slow");
                $("#confirmado_nuevo_partido").show("slide", {direction: "down" }, "slow").delay(5000);
                if(url_guardar == "nuevo_partido"){
                    //actualiza_pagina("nuevo");
                    $("#form_redireccion").delay(5000).submit();
                }
                else{
                    $("#confirmado_nuevo_partido").show("slide", {direction: "down" }, "slow");
                }

            }
            else{
                $("#error_nuevo_partido").show();
                $("#error_nuevo_partido_texto").html('<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> ' + r.error)
            }
        }
    });
}

function submit_nuevo_partido_cancelar(){
    //$("#btn-submit-partido").show("slow");
    $("#botonera_form_nuevo_partido").show("slide", {direction: "down" }, "slow");
    $("#advertencia_nuevo_partido").hide("slide", {direction: "up" }, "slow");
}

function editar_incluir_jugador(fila){
    $("#editar_incluir_jugador_"+fila).submit();
}

function activa_enlace_menu(id){
    $("#"+id).addClass("active");
}

function actualiza_estado_visible(elem){
    if($(elem).is(":checked")){
        $("#visible").val(1);
    }
    else{
        $("#visible").val(0);
    }
}

/************************************************************************************/
/* BUSCADOR DE PARTIDOS */
/************************************************************************************/

function busca_partidos(){
    if($("#id_fecha").val() == ""){
        $("#id_fecha").parent().addClass("has-error");
        $("#id_fecha").focus();
    }
    else{
        $("#form_buscador_partidos").submit();
    }
}

/*Desplazamiento animado, del origen ELEM al DESTINO*/
function desplaza(destino){
	$('html,body').animate({
    	scrollTop: $('#'+destino).offset().top
	}, 2000);
}

/************************************************************************************/
/* ADMINISTRACION DE CLUB */
/************************************************************************************/

function form_editar(id_titulo, id_form){
    //Vaciar filas de pistas eliminadas
    $("#ids_pistas_eliminadas").val("");
    $("#ids_nj_eliminadas").val("");
    $("#ids_deportes_eliminados").val("");
    $("#ids_fh_eliminadas").val("");

    //Ocultamos todos los formularios
    $(".formulario_administracion").hide();

    //Mostramos el que corresponde
    $("#"+id_form).show();
    $("#"+id_titulo).show();
    desplaza(id_titulo);
}

function actualiza_municipios(elem){
    var provincia_id = $(elem).val();
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

function submit_club(){
    var submit = true;
    if($("#id_nombre").val() == ""){
        $("#id_nombre").parent().addClass("has-error");
        submit = false;
    }
    else{
        $("#id_nombre").parent().removeClass("has-error");
    }
    if($("#id_provincia").val() == ""){
        $("#id_provincia").parent().addClass("has-error");
        submit = false;
    }
    else{
        $("#id_provincia").parent().removeClass("has-error");
    }
    if($("#id_municipio").val() == "" || $("#id_municipio").val() == 0){
        $("#id_municipio").parent().addClass("has-error");
        submit = false;
    }
    else{
        $("#id_municipio").parent().removeClass("has-error");
    }
    if($("#id_direccion").val() == ""){
        $("#id_direccion").parent().addClass("has-error");
        submit = false;
    }
    else{
        $("#id_direccion").parent().removeClass("has-error");
    }
    if($("#id_descripcion").val() == ""){
        $("#id_descripcion").parent().addClass("has-error");
        submit = false;
    }
    else{
        $("#id_descripcion").parent().removeClass("has-error");
    }

    if(submit){
        $("#form_club").submit();
    }
}

//Franjas horarias
function liberar_franja_horaria(franja_horaria_id){

    ocultar_efecto(".alerta_franja_horaria");
    ocultar("#btn_editar_"+franja_horaria_id);
    mostrar("#btn_guardar_"+franja_horaria_id);
    $(".select_fh_"+franja_horaria_id).attr("disabled", false);
}

function actualizar_franja_horaria(accion, franja_horaria_id){
    var form;
    var guardar = false;

    ocultar_efecto(".alerta_franja_horaria");

    if(accion == "nuevo"){
        form = $("#form_franja_hora_nueva");
        guardar = true;
        $(".validar").each(function(e){
            if($(this).val() == ""){
                $(this).parent().removeClass("has-success").addClass("has-error");
                guardar = false;
                return;
            }
            else{
                $(this).parent().removeClass("has-error").addClass("has-success");
            }
        });

    }
    else if(accion == "editar"){
        form = $("#form_franja_hora_"+franja_horaria_id);
        guardar = true;
    }
    else if(accion == "eliminar"){
        //Actualizar valor accion del formulario a eliminar
        $("#form_franja_hora_"+franja_horaria_id + " #action").val(accion);
        form = $("#form_franja_hora_"+franja_horaria_id);
        guardar = true;
    }

    if(guardar){
        guardar_franja_horaria(accion, franja_horaria_id, form);
    }
}

function guardar_franja_horaria(accion, franja_horaria_id, formulario){
    $.ajax({
        data: formulario.serialize(),
        url: formulario.attr("action"),
        type: 'POST',
        success: function(data){
            var r = JSON.parse(data);
            var id_texto, id_mensaje;

            if(accion == "nuevo"){
                id_texto = "texto_mensaje_nueva_franja_horaria";
                id_mensaje = "mensaje_nueva_franja_horaria";
            }
            else{
                id_texto = "texto_mensaje_franja_horaria_"+franja_horaria_id;
                id_mensaje = "mensaje_franja_horaria_"+franja_horaria_id;
            }

            if(r.error != null && r.error != ""){
                $("#"+id_texto).html(r.error);
                $("#"+id_texto).removeClass("alert-success").addClass("alert-error");
            }
            else{
                $("#"+id_texto).html("Se ha guardado la franja horaria correctamente");
                $("#"+id_texto).removeClass("alert-danger").addClass("alert-success");
            }
            mostrar_efecto("#"+id_mensaje);

            //Actualizar página si es una franja horaria nueva
            if(accion == "nuevo" && (r.error == null || r.error == "")){
                $("#actualizar").delay(5000).submit();
            }

            if(accion == "eliminar" && (r.error == null || r.error == "")){
                if($("#fila_form_franja_hora_"+franja_horaria_id).next().is("hr")){
                    $("#fila_form_franja_hora_"+franja_horaria_id).next().remove();
                }
                $("#fila_form_franja_hora_"+franja_horaria_id).delay(5000).remove();
            }

            if(accion == "editar"){
                $(".select_fh_"+franja_horaria_id).attr("disabled", "disabled");
                ocultar("#btn_guardar_"+franja_horaria_id);
                mostrar("#btn_editar_"+franja_horaria_id);
            }
        }
    });
}

//Niveles de juego
function liberar_nivel_juego(nivel_juego_id){

    ocultar_efecto(".alerta_nivel_juego");
    ocultar("#btn_editar_nj_"+nivel_juego_id);
    mostrar("#btn_guardar_nj_"+nivel_juego_id);
    $(".elemento_nivel_juego_"+nivel_juego_id).attr("disabled", false);
}

function actualizar_nivel_juego(accion, nivel_juego_id){
    var form;
    var guardar = false;

    ocultar_efecto(".alerta_nivel_juego");

    if(accion == "nuevo"){
        form = $("#form_nivel_juego_nuevo");
        guardar = true;
        $(".validar_nivel_juego").each(function(e){
            if($(this).val() == ""){
                $(this).parent().removeClass("has-success").addClass("has-error");
                guardar = false;
                return;
            }
            else{
                $(this).parent().removeClass("has-error").addClass("has-success");
            }
        });

    }
    else if(accion == "editar"){
        form = $("#form_nivel_juego_"+nivel_juego_id);
        if($("#id_nj_nivel_"+nivel_juego_id).val() != ""){
            guardar = true;
        }else{
            $("#id_nj_nivel_"+nivel_juego_id).parent().addClass("has-error");
        }
    }
    else if(accion == "eliminar"){
        //Actualizar valor accion del formulario a eliminar
        $("#form_nivel_juego_"+nivel_juego_id + " #action").val(accion);
        form = $("#form_nivel_juego_"+nivel_juego_id);
        guardar = true;
    }

    if(guardar){
        guardar_nivel_juego(accion, nivel_juego_id, form);
    }
}

function guardar_nivel_juego(accion, nivel_juego_id, formulario){
    $.ajax({
        data: formulario.serialize(),
        url: formulario.attr("action"),
        type: 'POST',
        success: function(data){
            var r = JSON.parse(data);
            var id_texto, id_mensaje;

            if(accion == "nuevo"){
                id_texto = "texto_mensaje_nuevo_nivel_juego";
                id_mensaje = "mensaje_nuevo_nivel_juego";
            }
            else{
                id_texto = "texto_mensaje_nivel_juego_"+nivel_juego_id;
                id_mensaje = "mensaje_nivel_juego_"+nivel_juego_id;
            }

            if(r.error != null && r.error != ""){
                $("#"+id_texto).html(r.error);
                $("#"+id_texto).removeClass("alert-success").addClass("alert-error");
            }
            else{
                $("#"+id_texto).html("Se ha guardado el nivel de juego correctamente");
                $("#"+id_texto).removeClass("alert-danger").addClass("alert-success");
            }
            mostrar_efecto("#"+id_mensaje);

            //Actualizar página si es una franja horaria nueva
            if(accion == "nuevo" && (r.error == null || r.error == "")){
                $("#actualizar").delay(5000).submit();
            }

            if(accion == "eliminar" && (r.error == null || r.error == "")){
                if($("#fila_form_nivel_juego_"+nivel_juego_id).next().is("hr")){
                    $("#fila_form_nivel_juego_"+nivel_juego_id).next().remove();
                }
                $("#fila_form_nivel_juego_"+nivel_juego_id).delay(5000).remove();
            }

            if(accion == "editar"){
                $(".has-error").removeClass("has-error");
                $(".elemento_nivel_juego_"+nivel_juego_id).attr("disabled", "disabled");
                ocultar("#btn_guardar_nj_"+nivel_juego_id);
                mostrar("#btn_editar_nj_"+nivel_juego_id);
            }
        }
    });
}

//Pistas
function liberar_pista(pista_id){

    ocultar_efecto(".alerta_pista");
    ocultar("#btn_editar_pista_"+pista_id);
    mostrar("#btn_guardar_pista_"+pista_id);
    $(".elemento_pista_"+pista_id).attr("disabled", false);
}

function actualizar_pista(accion, pista_id){
    var form;
    var guardar = false;

    ocultar_efecto(".alerta_pista");

    if(accion == "nuevo"){
        form = $("#form_pista_nuevo");
        guardar = true;
        $(".validar_pista").each(function(e){
            if($(this).val() == "" || ($(this).is("select") && $(this).find('option:selected').val() != "")){
                $(this).parent().removeClass("has-success").addClass("has-error");
                guardar = false;
                return;
            }
            else{
                $(this).parent().removeClass("has-error").addClass("has-success");
            }
        });

    }
    else if(accion == "editar"){
        form = $("#form_pista_"+pista_id);
        if($("#id_pista_orden_"+pista_id).val() != "" && $("#id_pista_deporte_"+pista_id).val() != "" && $("#id_pista_nombre_"+pista_id).val() != ""){
            guardar = true;
        }else{
            $("#id_pista_orden_"+pista_id).parent().addClass("has-error");
            $("#id_pista_deporte_"+pista_id).parent().addClass("has-error");
            $("#id_pista_nombre_"+pista_id).parent().addClass("has-error");
        }
    }
    else if(accion == "eliminar"){
        //Actualizar valor accion del formulario a eliminar
        $("#form_pista_"+pista_id + " #action").val(accion);
        form = $("#form_pista_"+pista_id);
        guardar = true;
    }

    if(guardar){
        guardar_pista(accion, pista_id, form);
    }
}

function guardar_pista(accion, pista_id, formulario){
    $.ajax({
        data: formulario.serialize(),
        url: formulario.attr("action"),
        type: 'POST',
        success: function(data){
            var r = JSON.parse(data);
            var id_texto, id_mensaje;

            if(accion == "nuevo"){
                id_texto = "texto_mensaje_nueva_pista";
                id_mensaje = "mensaje_nueva_pista";
            }
            else{
                id_texto = "texto_mensaje_pista_"+pista_id;
                id_mensaje = "mensaje_pista_"+pista_id;
            }

            if(r.error != null && r.error != ""){
                $("#"+id_texto).html(r.error);
                $("#"+id_texto).removeClass("alert-success").addClass("alert-error");
            }
            else{
                $("#"+id_texto).html("Se ha guardado la pista correctamente");
                $("#"+id_texto).removeClass("alert-danger").addClass("alert-success");
            }
            mostrar_efecto("#"+id_mensaje);

            //Actualizar página si es una franja horaria nueva
            if(accion == "nuevo" && (r.error == null || r.error == "")){
                $("#actualizar").delay(5000).submit();
            }

            if(accion == "eliminar" && (r.error == null || r.error == "")){
                if($("#fila_form_pista_"+pista_id).next().is("hr")){
                    $("#fila_form_pista_"+pista_id).next().remove();
                }
                $("#fila_form_pista_"+pista_id).delay(5000).remove();
            }

            if(accion == "editar"){
                $(".has-error").removeClass("has-error");
                $(".elemento_pista_"+pista_id).attr("disabled", "disabled");
                ocultar("#btn_guardar_pista_"+pista_id);
                mostrar("#btn_editar_pista_"+pista_id);
            }
        }
    });
}

function elimina_fila_pista(num_fila){
    if(confirm("¿Está seguro que desea eliminar esta pista? Se eliminarán todos los partidos que se han jugado o están programados en ella")){
        if($("#ids_pistas_eliminadas").val() == ""){
            $("#ids_pistas_eliminadas").val(num_fila);
        }
        else{
            $("#ids_pistas_eliminadas").val($("#ids_pistas_eliminadas").val() + "," + num_fila);
        }
        $("#fila_form_pista_"+num_fila).hide("slide", {direction: "up" }, "slow");
        //$("#fila_form_pista_"+num_fila).remove();
    }
}

function actualiza_pagina(url){
    //location.reload(true);
    //window.location.href = url;
    window.location.replace(url);
}

function esFechaMenorActual(date){
      var x = new Date();
      var fecha = date.split("/");
      x.setDate(fecha[0]);
      x.setMonth(fecha[1] - 1);
      x.setFullYear(fecha[2]);
      var today = new Date();

      if (x < today)
        return true;
      else
        return false;
}

/******************************************************************************/
/* Página principal */
/******************************************************************************/

function redirige_partido(usuario_id, pista_id){
    var num_jugadores = $("#num_jugadores_pista_"+pista_id).val();
    var partido_id = $("#partido_id_pista_"+pista_id).val();
    if(num_jugadores > 0 && partido_id != ""){
        window.location.href = usuario_id+"/partido/"+partido_id+"/editar";
    }
    else{
        window.location.href = +usuario_id+"/nuevo";
    }
}

function mostrar_contacto(){
    if($("#form_contacto").is(":visible")){
        $("#form_contacto").hide();
    }
    else{
        $("#form_contacto").show();
    }
}

/******************************************************************************/
/* Estadisticas */
/******************************************************************************/


function inicia_pagina_estadisticas(){
    incrementar_contadores_estadisticas();
}

function mostrarCapaOtraFecha(){
    if($("#id_varias_fechas").is(":checked")){
        $("#id_varias_fechas").val(1);
        $("#capa_otra_fecha").show();
    }
    else{
        $("#id_varias_fechas").val(0);
        $("#capa_otra_fecha").hide();
    }
}

/******************************************************************************/
/* Página de jugador */
/******************************************************************************/

function submit_mi_cuenta(){
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

/******************************************************************************/
/* Página de jugador */
/******************************************************************************/

function dar_baja_jugador(user_id, club_id){
    if(confirm("¿Está seguro que desea dar de baja a este jugador del club?")){
        $.ajax({
            data: {'jugador_id':user_id, 'club_id':club_id},
            url: '/baja_jugador_club',
            type: 'GET',
            success: function(data){
                var r = JSON.parse(data);
                if(r.res == "OK"){
                    $("#error_baja").hide();
                    $("#success_baja").show();
                }
                else{
                    $("#error_baja").show();
                    $("#success_baja").hide();
                }
            }
        });
    }
}

function form_crear_jugador(){
    $("#alta_jugador_titulo").show();
    $("#alta_jugador_form").show();
}

/******************************************************************************/
/* Página de notificaciones */
/******************************************************************************/

function marcar_como_leida(notif_id){
    $.ajax({
        data: {'notificacion_id':notif_id},
        url: '/marcar_leida',
        type: 'GET',
        success: function(data){
            var r = JSON.parse(data);
            if(r.error == ""){
                actualiza_css_notificacion_leida(notif_id);
            }
            else{
                $("#error_notificacion_texto_"+notif_id).html(r.error);
                $("#error_notificacion_"+notif_id).show();
            }
        }
    });
}

function inscripcion_clubes(notif_id, estado){
    $("#estado_id_"+notif_id).val(estado);
    $.ajax({
        data: $("#form_inscripcion_"+notif_id).serialize(),
        url: '/aceptar_denegar_inscripcion',
        type: 'POST',
        success: function(data){
            var r = JSON.parse(data);
            if(r.error == ""){
                if(estado == 1){
                    $("#btn_denegar_inscripcion_"+notif_id).hide("slide", {direction: "up" }, "slow");
                    $("#btn_aceptar_inscripcion_"+notif_id).html("Aceptada");
                    $("#btn_aceptar_inscripcion_"+notif_id).attr("disabled", "disabled");
                }
                else{
                    $("#btn_aceptar_inscripcion_"+notif_id).hide("slide", {direction: "up" }, "slow");
                    $("#btn_denegar_inscripcion_"+notif_id).html("Denegada");
                    $("#btn_denegar_inscripcion_"+notif_id).attr("disabled", "disabled");
                    $("#btn_denegar_inscripcion_"+notif_id).removeClass("btn-info");
                    $("#btn_denegar_inscripcion_"+notif_id).addClass("btn-danger");
                }
                actualiza_css_notificacion_leida(notif_id);
            }
            else{
                $("#error_notificacion_texto_"+notif_id).html(r.error);
                $("#error_notificacion_"+notif_id).show();
            }
        }
    });

    actualiza_css_notificacion_leida(notif_id);
}

function actualiza_css_notificacion_leida(notif_id){
    $("#panel_"+notif_id).removeClass("fondo-info");
    $("#texto_leida_"+notif_id).hide();
    $("#texto_leida_"+notif_id).remove();
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
    var form = $("#form_contacto_formulario").serialize();
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

/***************************************/
/* Administradores */
/***************************************/

function mostrar_ventana_modal_administradores(admin_id){
    $('#eliminar_administrador_modal').modal('show');
    $("#id_administrador_seleccionado").val(admin_id);
}

function mostrar_ventana_modal_asignar_administradores(jugador_id){
    $('#asignar_administrador_modal').modal('show');
    $("#id_jugador_asignado").val(jugador_id);
}