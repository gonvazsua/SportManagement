# -*- encoding: utf-8 -*-

######################################################
#Plantilla email para cambio de password
######################################################
def plantilla_email_pass(nombre_int, password_int):

    nombre = str(nombre_int)
    password = str(password_int)

    texto = ""
    texto += '<table width="100%" border="0" cellspacing="0" cellpadding="0">'
    texto += '  <tr>'
    texto += '    <td align="center" valign="top"><br>'
    texto += '		<br>'
    texto += '		<table width="600" border="0" cellspacing="0" cellpadding="0">'
    texto += '			<tr>'
    texto += '				<td align="left" valign="top" bgcolor="#ffffff" style="background-color:#ffffff;">'
    texto += '					<table width="570" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:15px;">'
    texto += '						<tr>'
    texto += '							<td align="left" valign="middle" style="padding:10px;">'
    texto += '								<h1 style=" color:#4e4e4e;">SportClick.club</h1>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '					<table width="570" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:15px;">'
    texto += '						<tr>'
    texto += '							<td width="360" align="left" valign="middle" style="font-family:Arial, Helvetica, sans-serif; color:#4e4e4e; font-size:13px; padding-right:10px;">'
    texto += '								<div style="font-size:24px;">Hola ' + nombre + '!<br><br></div>'
    texto += '								Parece que has perdido tu contraseña. A continuación te dejamos la nueva contraseña que te hemos generado. ¡No olvides cambiarla!'
    texto += '								<br><br>'
    texto += '								Tu nueva contraseña es: <strong>' + password + '</strong>'
    texto += '							</td>'
    texto += '							<td align="right" valign="middle">'
    texto += '								<table width="210" border="0" cellspacing="0" cellpadding="0">'
    texto += '									<tr>'
    texto += '										<td align="center" valign="top" bgcolor="#1ba5db" style="background-color:#1ba5db; padding-top: 20px; padding-bottom: 20px; border-top-left-radius: 15px; border-bottom-right-radius: 15px;">'
    texto += '											<table width="184" border="0" cellspacing="0" cellpadding="4">'
    texto += '												<tr>'
    texto += '												  <td align="left" valign="top" style="font-family:Arial, Helvetica, sans-serif; font-size:20px; color:#ffffff;"><b>Links rápidos</b></td>'
    texto += '												</tr>'
    texto += '												<tr>'
    texto += '													<td align="left" valign="top" style="font-family:Arial, Helvetica, sans-serif; font-size:12px; color:#ffffff;">'
    texto += '														<a href="http://www.sportclick.club" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Accede</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#services" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Servicios</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#contact" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Contacto</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#apartado_registro" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Registro</a>'
    texto += '													</td>'
    texto += '												</tr>'
    texto += '											</table>'
    texto += '										</td>'
    texto += '									</tr>'
    texto += '								</table>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '					<table width="95%" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">'
    texto += '						<tr>'
    texto += '							<td width="330" align="left" valign="middle" style="padding:10px;"></td>'
    texto += '							<td align="left" valign="middle" style="color:#595959; font-size:11px; font-family:Arial, Helvetica, sans-serif; padding:10px;"> '
    texto += '								<b>Dirección</b><br> '
    texto += '								<a href="http://www.sportclick.club" target="_blank"  style="color:#595959; text-decoration:none;">http://www.sportclick.club</a><br>'
    texto += '								<br>'
    texto += '								<b>Contacto:</b> <br>'
    texto += '								<a href="mailto:info@sportclick.club" style="color:#595959; text-decoration:none;">info@sportclick.club</a>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '				</td>'
    texto += '			</tr>'
    texto += '		</table>'
    texto += '		<br>'
    texto += '		<br>'
    texto += '	</td>'
    texto += '  </tr>'
    texto += '</table>'

    return texto

######################################################
#Plantilla email para cambio de password
######################################################
def plantilla_email_registro(nombre_int, usuario_int, password_int):

    nombre = str(nombre_int)
    password = str(password_int)
    usuario = str(usuario_int)

    texto = ""
    texto += '<table width="100%" border="0" cellspacing="0" cellpadding="0">'
    texto += '  <tr>'
    texto += '    <td align="center" valign="top"><br>'
    texto += '		<br>'
    texto += '		<table width="600" border="0" cellspacing="0" cellpadding="0">'
    texto += '			<tr>'
    texto += '				<td align="left" valign="top" bgcolor="#ffffff" style="background-color:#ffffff;">'
    texto += '					<table width="570" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:15px;">'
    texto += '						<tr>'
    texto += '							<td align="left" valign="middle" style="padding:10px;">'
    texto += '								<h1 style=" color:#4e4e4e;">Bienvenido a SportClick.club</h1>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '					<table width="570" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:15px;">'
    texto += '						<tr>'
    texto += '							<td width="360" align="left" valign="middle" style="font-family:Arial, Helvetica, sans-serif; color:#4e4e4e; font-size:13px; padding-right:10px;">'
    texto += '								<div style="font-size:24px;">Hola ' + nombre + '!<br><br></div>'
    texto += '								Bienvenido a SportClick. Utiliza nuestros servicios para no quedarte sin jugar ni un solo día<br>'
    texto += '								Estos son los datos con los que te has dado de alta:'
    texto += '								<br><br>'
    texto += '								Nombre de usuario: <strong>' + usuario + '</strong><br>'
    texto += '								Contraseña: <strong>' + password + '</strong>'
    texto += '							</td>'
    texto += '							<td align="right" valign="middle">'
    texto += '								<table width="210" border="0" cellspacing="0" cellpadding="0">'
    texto += '									<tr>'
    texto += '										<td align="center" valign="top" bgcolor="#1ba5db" style="background-color:#1ba5db; padding-top: 20px; padding-bottom: 20px; border-top-left-radius: 15px; border-bottom-right-radius: 15px;">'
    texto += '											<table width="184" border="0" cellspacing="0" cellpadding="4">'
    texto += '												<tr>'
    texto += '												  <td align="left" valign="top" style="font-family:Arial, Helvetica, sans-serif; font-size:20px; color:#ffffff;"><b>Links rápidos</b></td>'
    texto += '												</tr>'
    texto += '												<tr>'
    texto += '													<td align="left" valign="top" style="font-family:Arial, Helvetica, sans-serif; font-size:12px; color:#ffffff;">'
    texto += '														<a href="http://www.sportclick.club" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Accede</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#services" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Servicios</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#contact" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Contacto</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#apartado_registro" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Registro</a>'
    texto += '													</td>'
    texto += '												</tr>'
    texto += '											</table>'
    texto += '										</td>'
    texto += '									</tr>'
    texto += '								</table>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '					<table width="95%" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">'
    texto += '						<tr>'
    texto += '							<td width="330" align="left" valign="middle" style="padding:10px;"></td>'
    texto += '							<td align="left" valign="middle" style="color:#595959; font-size:11px; font-family:Arial, Helvetica, sans-serif; padding:10px;"> '
    texto += '								<b>Dirección</b><br> '
    texto += '								<a href="http://www.sportclick.club" target="_blank"  style="color:#595959; text-decoration:none;">http://www.sportclick.club</a><br>'
    texto += '								<br>'
    texto += '								<b>Contacto:</b> <br>'
    texto += '								<a href="mailto:info@sportclick.club" style="color:#595959; text-decoration:none;">info@sportclick.club</a>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '				</td>'
    texto += '			</tr>'
    texto += '		</table>'
    texto += '		<br>'
    texto += '		<br>'
    texto += '	</td>'
    texto += '  </tr>'
    texto += '</table>'

    return texto

######################################################
#Plantilla email para cambio de password
######################################################
def plantilla_email_partido(nombre_int, partido):

    nombre = nombre_int
    hora = partido.franja_horaria.inicio.strftime('%H:%M')
    fecha = partido.fecha.strftime('%d, %b %Y')
    club_nombre = partido.pista.club.nombre
    deporte = partido.pista.deporte.deporte
    pista_nombre = partido.pista.nombre

    texto = ""
    texto += '<table width="100%" border="0" cellspacing="0" cellpadding="0">'
    texto += '  <tr>'
    texto += '    <td align="center" valign="top"><br>'
    texto += '		<br>'
    texto += '		<table width="600" border="0" cellspacing="0" cellpadding="0">'
    texto += '			<tr>'
    texto += '				<td align="left" valign="top" bgcolor="#ffffff" style="background-color:#ffffff;">'
    texto += '					<table width="570" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:15px;">'
    texto += '						<tr>'
    texto += '							<td align="left" valign="middle" style="padding:10px;">'
    texto += '								<h1 style=" color:#4e4e4e;">SportClick.club</h1>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '					<table width="570" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:15px;">'
    texto += '						<tr>'
    texto += '							<td width="360" align="left" valign="middle" style="font-family:Arial, Helvetica, sans-serif; color:#4e4e4e; font-size:13px; padding-right:10px;">'
    texto += '								<div style="font-size:24px;">Hola ' + nombre + '!<br><br></div>'
    texto += '								El club <strong>"' + club_nombre + '"</strong> ha indicado que vas a jugar un partido de ' + deporte + '.<br>'
    texto += '								Estos son los datos del partido:'
    texto += '								<br><br>'
    texto += '								<strong>Fecha: </strong>' + fecha + '<br>'
    texto += '								<strong>Hora: </strong>' + hora + 'h<br>'
    texto += '								<strong>Pista: </strong>' + pista_nombre + '<br><br>'
    if len(partido.perfiles.all()) > 0:
        texto += 'Jugadores: <br>'
        for jugador in partido.perfiles.all():
            nombre_jugador = jugador.user.first_name
            apellidos = jugador.user.last_name
            #apellidos = apellidos.decode('iso-8859-1').encode('utf8')
            texto += '- ' + nombre_jugador + " " + apellidos + '<br>'
    else:
        texto += 'Todavía no hay jugadores confirmados'
    texto += '							</td>'
    texto += '							<td align="right" valign="middle">'
    texto += '								<table width="210" border="0" cellspacing="0" cellpadding="0">'
    texto += '									<tr>'
    texto += '										<td align="center" valign="top" bgcolor="#1ba5db" style="background-color:#1ba5db; padding-top: 20px; padding-bottom: 20px; border-top-left-radius: 15px; border-bottom-right-radius: 15px;">'
    texto += '											<table width="184" border="0" cellspacing="0" cellpadding="4">'
    texto += '												<tr>'
    texto += '												  <td align="left" valign="top" style="font-family:Arial, Helvetica, sans-serif; font-size:20px; color:#ffffff;"><b>Links</b></td>'
    texto += '												</tr>'
    texto += '												<tr>'
    texto += '													<td align="left" valign="top" style="font-family:Arial, Helvetica, sans-serif; font-size:12px; color:#ffffff;">'
    texto += '														<a href="http://www.sportclick.club" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Accede</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#services" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Servicios</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#contact" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Contacto</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#apartado_registro" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Registro</a>'
    texto += '													</td>'
    texto += '												</tr>'
    texto += '											</table>'
    texto += '										</td>'
    texto += '									</tr>'
    texto += '								</table>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '					<table width="95%" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">'
    texto += '						<tr>'
    texto += '							<td width="330" align="left" valign="middle" style="padding:10px;"></td>'
    texto += '							<td align="left" valign="middle" style="color:#595959; font-size:11px; font-family:Arial, Helvetica, sans-serif; padding:10px;"> '
    texto += '                              <b>Sitio web</b><br>'
    texto += '								<a href="http://www.sportclick.club" target="_blank"  style="color:#595959; text-decoration:none;">http://www.sportclick.club</a><br>'
    texto += '								<br>'
    texto += '								<b>Contacto:</b> <br>'
    texto += '								<a href="mailto:info@sportclick.club" style="color:#595959; text-decoration:none;">info@sportclick.club</a>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '				</td>'
    texto += '			</tr>'
    texto += '		</table>'
    texto += '		<br>'
    texto += '		<br>'
    texto += '	</td>'
    texto += '  </tr>'
    texto += '</table>'

    return texto


######################################################
#Plantilla email para modificaciones del partido
######################################################
def plantilla_email_editar_partido(nombre_int, partido):

    nombre = nombre_int
    hora = partido.franja_horaria.inicio.strftime('%H:%M')
    fecha = partido.fecha.strftime('%d, %b %Y')
    club_nombre = partido.pista.club.nombre
    deporte = partido.pista.deporte.deporte
    pista_nombre = partido.pista.nombre

    texto = ""
    texto += '<table width="100%" border="0" cellspacing="0" cellpadding="0">'
    texto += '  <tr>'
    texto += '    <td align="center" valign="top"><br>'
    texto += '		<br>'
    texto += '		<table width="600" border="0" cellspacing="0" cellpadding="0">'
    texto += '			<tr>'
    texto += '				<td align="left" valign="top" bgcolor="#ffffff" style="background-color:#ffffff;">'
    texto += '					<table width="570" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:15px;">'
    texto += '						<tr>'
    texto += '							<td align="left" valign="middle" style="padding:10px;">'
    texto += '								<h1 style=" color:#4e4e4e;">SportClick.club</h1>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '					<table width="570" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:15px;">'
    texto += '						<tr>'
    texto += '							<td width="360" align="left" valign="middle" style="font-family:Arial, Helvetica, sans-serif; color:#4e4e4e; font-size:13px; padding-right:10px;">'
    texto += '								<div style="font-size:24px;">Hola ' + nombre + '!<br><br></div>'
    texto += '								El club <strong>"' + club_nombre + '"</strong> ha modificado un partido de ' + deporte + ' en el que juegas.<br>'
    texto += '								Estos son los datos del partido:'
    texto += '								<br><br>'
    texto += '								<strong>Fecha: </strong>' + fecha + '<br>'
    texto += '								<strong>Hora: </strong>' + hora + 'h<br>'
    texto += '								<strong>Pista: </strong>' + pista_nombre + '<br><br>'
    if len(partido.perfiles.all()) > 0:
        texto += 'Jugadores: <br>'
        for jugador in partido.perfiles.all():
            nombre_jugador = jugador.user.first_name
            apellidos = jugador.user.last_name
            #apellidos = apellidos.decode('iso-8859-1').encode('utf8')
            texto += '- ' + nombre_jugador + " " + apellidos + '<br>'
    else:
        texto += 'Todavía no hay jugadores confirmados'
    texto += '							</td>'
    texto += '							<td align="right" valign="middle">'
    texto += '								<table width="210" border="0" cellspacing="0" cellpadding="0">'
    texto += '									<tr>'
    texto += '										<td align="center" valign="top" bgcolor="#1ba5db" style="background-color:#1ba5db; padding-top: 20px; padding-bottom: 20px; border-top-left-radius: 15px; border-bottom-right-radius: 15px;">'
    texto += '											<table width="184" border="0" cellspacing="0" cellpadding="4">'
    texto += '												<tr>'
    texto += '												  <td align="left" valign="top" style="font-family:Arial, Helvetica, sans-serif; font-size:20px; color:#ffffff;"><b>Links</b></td>'
    texto += '												</tr>'
    texto += '												<tr>'
    texto += '													<td align="left" valign="top" style="font-family:Arial, Helvetica, sans-serif; font-size:12px; color:#ffffff;">'
    texto += '														<a href="http://www.sportclick.club" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Accede</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#services" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Servicios</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#contact" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Contacto</a>'
    texto += '														<hr style="color:#FFFFFF;height:1px;">'
    texto += '														<a href="http://www.sportclick.club#apartado_registro" style="color:#ffffff; text-decoration:underline; text-decoration:none;">Registro</a>'
    texto += '													</td>'
    texto += '												</tr>'
    texto += '											</table>'
    texto += '										</td>'
    texto += '									</tr>'
    texto += '								</table>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '					<table width="95%" border="0" align="center" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">'
    texto += '						<tr>'
    texto += '							<td width="330" align="left" valign="middle" style="padding:10px;"></td>'
    texto += '							<td align="left" valign="middle" style="color:#595959; font-size:11px; font-family:Arial, Helvetica, sans-serif; padding:10px;"> '
    texto += '                              <b>Sitio web</b><br>'
    texto += '								<a href="http://www.sportclick.club" target="_blank"  style="color:#595959; text-decoration:none;">http://www.sportclick.club</a><br>'
    texto += '								<br>'
    texto += '								<b>Contacto:</b> <br>'
    texto += '								<a href="mailto:info@sportclick.club" style="color:#595959; text-decoration:none;">info@sportclick.club</a>'
    texto += '							</td>'
    texto += '						</tr>'
    texto += '					</table>'
    texto += '				</td>'
    texto += '			</tr>'
    texto += '		</table>'
    texto += '		<br>'
    texto += '		<br>'
    texto += '	</td>'
    texto += '  </tr>'
    texto += '</table>'

    return texto