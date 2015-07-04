# -*- encoding: utf-8 -*-
from django import forms

class formulario_login(forms.Form):
    username = forms.CharField(
        required=True, widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    password = forms.CharField(
        required=True, widget= forms.PasswordInput(attrs={'type':'password','class': 'form-control', 'placeholder': 'Contraseña'})
    )

class formulario_registro(forms.Form):
    nombre = forms.CharField(
        required=True, widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    apellidos = forms.CharField(
        required=True, widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    username = forms.CharField(
        required=True, widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    email = forms.CharField(
        required=True, widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'type': 'email'})
    )
    password1 = forms.CharField(
        required=True, widget= forms.PasswordInput(attrs={'type':'password','class': 'form-control', 'placeholder': 'Contraseña'})
    )
    password2 = forms.CharField(
        required=True, widget= forms.PasswordInput(attrs={'type':'password','class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )

class FormBuscador(forms.Form):
    nombre = forms.CharField(
        widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    apellidos = forms.CharField(
        widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    username = forms.CharField(
        widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    email = forms.CharField(
        widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'type': 'email'})
    )

class FormAdministracionClub(forms.Form):
    nombre = forms.CharField(
        widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del club'})
    )
    descripcion = forms.CharField(
        widget= forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'})
    )
    direccion = forms.CharField(
        widget= forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'})
    )

class FormImagen(forms.Form):
    imagen = forms.ImageField()
