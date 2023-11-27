import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private usuariosRegistradosKey = 'usuariosRegistrados';

  registrar(usuario: any): void {
    // Obtener el valor almacenado en localStorage
    const storedData = localStorage.getItem(this.usuariosRegistradosKey);
  
    // Verificar si el valor obtenido no es nulo
    if (storedData !== null) {
      try {
        // Intentar realizar el JSON.parse
        const usuariosRegistrados: any[] = JSON.parse(storedData);
  
        // Agregar el nuevo usuario
        usuariosRegistrados.push(usuario);
  
        // Guardar en localStorage
        localStorage.setItem(this.usuariosRegistradosKey, JSON.stringify(usuariosRegistrados));
      } catch (error) {
        console.error('Error al parsear JSON:', error);
        // Manejar el error de manera adecuada, según tus necesidades
      }
    } else {
      // Si el valor es nulo, crear un nuevo array con el usuario y guardarlo en localStorage
      localStorage.setItem(this.usuariosRegistradosKey, JSON.stringify([usuario]));
    }
  }

  // Método para verificar la existencia de un usuario
  login(correo: string, password: string): boolean {
    // Obtener el valor almacenado en localStorage
    const storedData = localStorage.getItem(this.usuariosRegistradosKey);
  
    // Verificar si el valor obtenido no es nulo
    if (storedData !== null) {
      try {
        // Intentar realizar el JSON.parse
        const usuariosRegistrados: any[] = JSON.parse(storedData);
  
        // Verificar si existe un usuario con el correo y la contraseña proporcionados
        const usuario = usuariosRegistrados.find(u => u.correo === correo && u.password === password);
  
        // Si se encuentra un usuario, devolver true, de lo contrario, devolver false
        return !!usuario;
      } catch (error) {
        console.error('Error al parsear JSON:', error);
        // Manejar el error de manera adecuada, según tus necesidades
        return false; // Devolver false en caso de error
      }
    } else {
      // Si el valor es nulo, no hay usuarios registrados, devolver false
      return false;
    }
  }

  // Método para cerrar sesión (eliminar datos del usuario del localStorage)
  logout(): void {
    localStorage.removeItem(this.usuariosRegistradosKey);
  }
  isAuthenticated(): boolean {
    // Obtener el valor almacenado en localStorage
    const storedData = localStorage.getItem(this.usuariosRegistradosKey);
  
    // Verificar si el valor obtenido no es nulo
    if (storedData !== null) {
      try {
        // Intentar realizar el JSON.parse
        const usuariosRegistrados: any[] = JSON.parse(storedData);
  
        // Verificar si hay al menos un usuario registrado
        return usuariosRegistrados.length > 0;
      } catch (error) {
        console.error('Error al parsear JSON:', error);
        // Manejar el error de manera adecuada, según tus necesidades
        return false; // Devolver false en caso de error
      }
    } else {
      // Si el valor es nulo, no hay usuarios registrados, devolver false
      return false;
    }
  }
  getUsuarioAutenticado(): any {
    const storedData = localStorage.getItem(this.usuariosRegistradosKey);
    if (storedData !== null) {
      try {
        // Intentar realizar el JSON.parse
        const usuariosRegistrados: any[] = JSON.parse(storedData);
  
        // Verificar si hay al menos un usuario registrado
        return usuariosRegistrados.length > 0 ? usuariosRegistrados[0] : null;
      } catch (error) {
        console.error('Error al parsear JSON:', error);
        // Manejar el error de manera adecuada, según tus necesidades
        return false; // Devolver false en caso de error
      }
    } else {
      // Si el valor es nulo, no hay usuarios registrados, devolver false
      return false;
    }
  }
  constructor() { }
}
