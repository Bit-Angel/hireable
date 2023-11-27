import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  formularioLogin: FormGroup;

  constructor(private fb: FormBuilder, private authService: AuthService, private router: Router) {
    this.formularioLogin = this.fb.group({
      correo: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  ngOnInit(): void {
  }

  iniciarSesion(): void {
    const correoControl = this.formularioLogin.get('correo');
    const passwordControl = this.formularioLogin.get('password');
    if (correoControl && passwordControl) {
      const correo = correoControl.value;
      const password = passwordControl.value;
    
      if (this.authService.login(correo, password)) {
        // Iniciar sesión exitosa, puedes redirigir a otra página aquí
        this.router.navigate(['../empleos']);
      } else {
        // Manejar inicio de sesión fallido (puede mostrar un mensaje de error)
        alert(`Error de inicio de sesion, usuario no encontrado`);
        this.router.navigate(['../registro']);
      }
    } else {
      console.error('No se encontraron controles de formulario');
    }
  }

}
