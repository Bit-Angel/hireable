import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

interface Job {
  idOferta: number;
  image: string;
  position: string;
  company: string;
  salary: string;
  category: string;
  discapacidad: string;
}

@Component({
  selector: 'app-empleos',
  templateUrl: './empleos.component.html',
  styleUrls: ['./empleos.component.css']
})

export class EmpleosComponent implements OnInit {
  jobList = [
    {
      idOferta: 1,
      image: '../../assets/image/E1.png',
      position: 'Gerente de Ventas',
      company: 'McDonalds',
      salary: '10K - 15K Mensuales',
      category: 'Servicios de Alimentos',
      discapacidad: 'Visual'
    },
    {
      idOferta: 2,
      image: '../../assets/image/E2.png',
      position: 'Auxiliar Admin.',
      company: 'Lala Mexico',
      salary: '14k - 15k Mensuales',
      category: 'Servicios de Alimentos',
      discapacidad: 'Auditiva'
    },
    {
      idOferta: 3,
      image: '../../assets/image/E3.png',
      position: 'Operador de Planta',
      company: 'Nissan',
      salary: '22k - 25k Mensuales',
      category: 'Servicios Automotriz',
      discapacidad: 'Automotriz'
    },
    {
      idOferta: 4,
      image: '../../assets/image/E4.png',
      position: 'Jardinero',
      company: 'UAA',
      salary: '7k - 9k Mensuales',
      category: 'Servicios de Jardineria',
      discapacidad: 'Automotriz'
    },
    {
      idOferta: 5,
      image: '../../assets/image/E5.png',
      position: 'Gerente de Ventas',
      company: 'Softtek',
      salary: '10k - 15k Mensuales',
      category: 'Servicios de TI',
      discapacidad: 'Automotriz'
    },
    {
      idOferta: 6,
      image: '../../assets/image/E5.png',
      position: 'Secretaria',
      company: 'Softtek',
      salary: '10k - 15k Mensuales',
      category: 'Servicios de TI',
      discapacidad: 'Automotriz'
    },
    {
      idOferta: 7,
      image: '../../assets/image/E6.png',
      position: 'Repartidor',
      company: 'Coca Cola.',
      salary: '20k - 25k Mensuales',
      category: 'Servicios de Alimentos',
      discapacidad: 'Automotriz'
    },
    {
      idOferta: 8,
      image: '../../assets/image/E7.png',
      position: 'Operador de Maquinaria',
      company: 'Pepsi',
      salary: '22k - 27k Mensuales',
      category: 'Servicios de Alimentos',
      discapacidad: 'Automotriz'
    },
    {
      idOferta: 9,
      image: '../../assets/image/E8.png',
      position: 'Secretario',
      company: 'Gobierno del Estado',
      salary: '22k - 25k Mensuales',
      category: 'Servicios',
      discapacidad: 'Automotriz'
    },
  ];

  selectedCapability: string = '';
  uniqueCapabilities: string[] = [];
  filteredJobList: Job[] = [];

  constructor(private authService: AuthService, private router: Router) {
    this.uniqueCapabilities = this.getUniqueCapabilities();
    this.filteredJobList = this.jobList;
  }

  getUniqueCapabilities() {
    const capabilities = new Set<string>();
    this.jobList.forEach(job => capabilities.add(job.discapacidad.toLowerCase()));
    return Array.from(capabilities);
  }

  filterByCapability() {
    const selectedCapabilityLower = this.selectedCapability.toLowerCase();
    this.filteredJobList = this.selectedCapability
      ? this.jobList.filter(job => job.discapacidad.toLowerCase() === selectedCapabilityLower)
      : this.jobList;
  }

  ngOnInit(): void {
    if (!this.authService.isAuthenticated()) {
      // Si no está autenticado, redirigir a otra página (por ejemplo, la página de inicio de sesión)
      this.router.navigate(['../login']);
    }
  }

}
