import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  usuarioAutenticado: any;
  title = 'hireable';

  constructor(private router: Router,private authService: AuthService) {}

  ngOnInit(): void {
    // Obtener información del usuario autenticado al inicializar el componente
    this.usuarioAutenticado = this.authService.getUsuarioAutenticado();
  }

  isAuthenticated(): boolean {
    return this.authService.isAuthenticated();
  }
  
  navegarARuta(ruta: string) {
    this.router.navigate([ruta]);
  }
}
