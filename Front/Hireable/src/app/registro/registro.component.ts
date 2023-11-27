import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-registro',
  templateUrl: './registro.component.html',
  styleUrls: ['./registro.component.css']
})
export class RegistroComponent implements OnInit {

  formularioRegistro: FormGroup;

  constructor(private authService: AuthService, private router: Router, private fb: FormBuilder) {
    this.formularioRegistro = this.fb.group({
      nombre: ['', Validators.required],
      correo: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      telefono: ['', Validators.required],
      discapacidad: ['ninguna', Validators.required],
      curriculum: [null, Validators.required],
  });
   }

  ngOnInit(): void {
  }

  registrarUsuario(): void {
    if (this.formularioRegistro.valid) {
        // Obtén los valores del formulario y realiza el registro
        const usuario = this.formularioRegistro.value;
        this.authService.registrar(usuario);

        // Redirigir a la nueva ruta después de registrar el usuario
        this.router.navigate(['../empleos']);
    } else {
        // El formulario no es válido, puedes realizar acciones adicionales si es necesario
        console.log('Formulario no válido');
    }
}
}
