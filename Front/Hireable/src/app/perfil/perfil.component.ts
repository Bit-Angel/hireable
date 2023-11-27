import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-perfil',
  templateUrl: './perfil.component.html',
  styleUrls: ['./perfil.component.css']
})
export class PerfilComponent implements OnInit {
  usuarioAutenticado: any;

  constructor(private authService: AuthService, private router: Router) { }

  ngOnInit(): void {
    this.usuarioAutenticado = this.authService.getUsuarioAutenticado();
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['../menu']);
    // Puedes redirigir a otra página después del cierre de sesión si es necesario
  }
}
