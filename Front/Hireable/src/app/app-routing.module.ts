import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

// Importación de componentes
import { MenubarComponent } from './menubar/menubar.component';
import { LoginComponent } from './login/login.component';
import { RegistroComponent } from './registro/registro.component';
import { NosotrosComponent } from './nosotros/nosotros.component';
import { EmpleosComponent } from './empleos/empleos.component';
import { MoreinfoComponent } from './moreinfo/moreinfo.component';
import { PerfilComponent } from './perfil/perfil.component';

const routes: Routes = [
  { path: 'menu', component: MenubarComponent },
  { path: 'login', component: LoginComponent },
  { path: 'registro', component: RegistroComponent },
  { path: 'nosotros', component: NosotrosComponent },
  { path: 'empleos', component: EmpleosComponent },
  { path: 'info/:idOferta', component: MoreinfoComponent },
  { path: 'perfil', component: PerfilComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
