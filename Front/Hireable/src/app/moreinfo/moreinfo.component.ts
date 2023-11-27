import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

interface Job {
  idOferta: number;
  image: string;
  position: string;
  company: string;
  salary: string;
  category: string;
  discapacidad: string;
  descripcion: string;
}

@Component({
  selector: 'app-moreinfo',
  templateUrl: './moreinfo.component.html',
  styleUrls: ['./moreinfo.component.css']
})
export class MoreinfoComponent implements OnInit {
  disableApplyButton = false;
  
  jobList: Job[] = [
    {
      idOferta: 1,
      image: '../../assets/image/E1.png',
      position: 'Gerente de Ventas',
      company: 'McDonalds',
      salary: '10K - 15K Mensuales',
      category: 'Servicios de Alimentos',
      discapacidad: 'Visual',
      descripcion: 'Como Gerente de Ventas en McDonalds, tendrás un rol clave en el impulso y la gestión del departamento de ventas de la empresa. Tendrás la responsabilidad de liderar y supervisar al equipo de ventas, así como de desarrollar e implementar estrategias para maximizar las ventas y alcanzar los objetivos establecidos.Tus responsabilidades incluirán la planificación y ejecución de campañas promocionales, la supervisión del desempeño de los empleados de ventas, la identificación de oportunidades de crecimiento y la implementación de tácticas para incrementar la rentabilidad. Además, serás responsable de establecer relaciones sólidas con los clientes, asegurándote de brindar un excelente servicio y de mantener altos estándares de calidad.'
    },
    {
      idOferta: 2,
      image: '../../assets/image/E2.png',
      position: 'Auxiliar Admin.',
      company: 'Lala Mexico',
      salary: '14k - 15k Mensuales',
      category: 'Servicios de Alimentos',
      discapacidad: 'Auditiva',
      descripcion: 'El personal auxiliar administrativo en Lala desempeña un papel esencial en el apoyo eficiente de las tareas administrativas. Sus responsabilidades incluyen la recepción y atención de visitantes, la gestión de documentos, la atención telefónica y por correo electrónico, la coordinación de agendas y reuniones, el manejo de suministros de oficina, el apoyo en tareas contables y administrativas, la asistencia en temas de recursos humanos y la mantención del orden en el área de trabajo. Su labor contribuye al buen funcionamiento y organización de la empresa.'
    },
    {
      idOferta: 3,
      image: '../../assets/image/E3.png',
      position: 'Operador de Planta',
      company: 'Nissan',
      salary: '22k - 25k Mensuales',
      category: 'Servicios Automotriz',
      discapacidad: 'Automotriz',
      descripcion: 'Un operador de planta de Nissan desempeña diversas tareas clave en la producción automotriz, como la operación de maquinaria especializada, el ensamblaje de componentes, la inspección de calidad y el mantenimiento básico. Su labor implica garantizar el cumplimiento de estándares de seguridad y eficiencia, así como la optimización de los procesos de fabricación. Además, colabora estrechamente con un equipo multidisciplinario, fomentando un ambiente de trabajo colaborativo y dinámico. El valor de trabajar en Nissan radica en la oportunidad de contribuir al desarrollo de vehículos innovadores, la formación profesional continua y la participación en una marca reconocida a nivel global.'
    },
    {
      idOferta: 4,
      image: '../../assets/image/E4.png',
      position: 'Jardinero',
      company: 'UAA',
      salary: '7k - 9k Mensuales',
      category: 'Servicios de Jardineria',
      discapacidad: 'Automotriz',
      descripcion: 'Un operador de planta de Nissan desempeña diversas tareas clave en la producción automotriz, como la operación de maquinaria especializada, el ensamblaje de componentes, la inspección de calidad y el mantenimiento básico. Su labor implica garantizar el cumplimiento de estándares de seguridad y eficiencia, así como la optimización de los procesos de fabricación. Además, colabora estrechamente con un equipo multidisciplinario, fomentando un ambiente de trabajo colaborativo y dinámico. El valor de trabajar en Nissan radica en la oportunidad de contribuir al desarrollo de vehículos innovadores, la formación profesional continua y la participación en una marca reconocida a nivel global.'
    },
    {
      idOferta: 5,
      image: '../../assets/image/E5.png',
      position: 'Gerente de Ventas',
      company: 'Softtek',
      salary: '10k - 15k Mensuales',
      category: 'Servicios de TI',
      discapacidad: 'Automotriz',
      descripcion: 'Como gerente de ventas en Softtek, tu responsabilidad principal sería liderar y supervisar las estrategias de ventas para impulsar el crecimiento y la expansión de los servicios de tecnología de la información (TI). Deberías establecer relaciones sólidas con clientes potenciales y existentes, identificar oportunidades de negocio, y colaborar estrechamente con el equipo de ventas para alcanzar objetivos y metas. Además, gestionarías eficientemente el ciclo de ventas completo, desde la identificación de oportunidades hasta el cierre de contratos, asegurando la satisfacción del cliente y contribuyendo al éxito general de la empresa en el mercado de servicios de TI.'
    },
    {
      idOferta: 6,
      image: '../../assets/image/E5.png',
      position: 'Secretaria',
      company: 'Softtek',
      salary: '10k - 15k Mensuales',
      category: 'Servicios de TI',
      discapacidad: 'Automotriz',
      descripcion: 'Como secretaria en Softtek, tu rol sería crucial para garantizar el funcionamiento eficiente de las operaciones diarias. Tendrías la responsabilidad de manejar la correspondencia, programar reuniones, y gestionar las comunicaciones internas y externas de la oficina. Además, colaborarías estrechamente con los equipos internos, proporcionando soporte administrativo y asegurando que los procesos de documentación y archivo se realicen de manera organizada y efectiva. Tu papel también podría incluir la coordinación de viajes y la preparación de informes, contribuyendo así al ambiente de trabajo productivo y al éxito general de Softtek. La habilidad para mantener la confidencialidad y la eficacia en la gestión de múltiples tareas serían aspectos clave de tu desempeño'
    },
    {
      idOferta: 7,
      image: '../../assets/image/E6.png',
      position: 'Repartidor',
      company: 'Coca Cola.',
      salary: '20k - 25k Mensuales',
      category: 'Servicios de Alimentos',
      discapacidad: 'Automotriz',
      descripcion: 'Como repartidor de Coca Cola, tu función principal sería asegurar la distribución efectiva y oportuna de los productos de la empresa a los clientes y puntos de venta asignados. Esto implicaría cargar, transportar y entregar los productos, garantizando la integridad de la mercancía durante todo el proceso. También serías responsable de mantener un registro preciso de las entregas, gestionar las transacciones y, en muchos casos, interactuar directamente con los clientes para mantener relaciones positivas. La eficiencia en la planificación de rutas, la atención a los plazos de entrega y el mantenimiento adecuado del vehículo de reparto serían aspectos clave de tu desempeño. Además, podrías ser parte integral de la representación de la marca Coca Cola, contribuyendo a la satisfacción del cliente y al éxito general de la empresa en el mercado.'
    },
    {
      idOferta: 8,
      image: '../../assets/image/E7.png',
      position: 'Operador de Maquinaria',
      company: 'Pepsi',
      salary: '22k - 27k Mensuales',
      category: 'Servicios de Alimentos',
      discapacidad: 'Automotriz',
      descripcion: 'Como operador de maquinaria en Pepsi, tu papel principal sería supervisar y operar maquinaria especializada utilizada en la producción y embotellado de productos. Serías responsable de asegurar que las máquinas funcionen de manera eficiente y segura, realizando ajustes y mantenimientos según sea necesario. Además, serías clave en la identificación y solución de problemas técnicos para minimizar el tiempo de inactividad de la maquinaria.'
    },
    {
      idOferta: 9,
      image: '../../assets/image/E8.png',
      position: 'Secretario',
      company: 'Gobierno del Estado',
      salary: '22k - 25k Mensuales',
      category: 'Servicios',
      discapacidad: 'Automotriz',
      descripcion: 'Como secretario en el Gobierno del Estado de Aguascalientes, desempeñarías un papel crucial en el apoyo administrativo y la coordinación de actividades esenciales para el funcionamiento eficiente de la oficina. Tendrías la responsabilidad de gestionar la correspondencia oficial, programar reuniones y mantener comunicaciones efectivas tanto internas como externas.'
    },
  ];
  
  job: Job | undefined;

  constructor( private route: ActivatedRoute,
    private location: Location) { }

  ngOnInit(): void {
    this.getJobDetails();
  }

  getJobDetails(): void {
    const idOferta = Number(this.route.snapshot.paramMap.get('idOferta'));  // Convertido a número
    if (!isNaN(idOferta)) {
      this.job = this.jobList.find(job => job.idOferta === idOferta);
    }
  }

  goBack(): void {
    this.location.back();
  }

  applyToJob(): void {
    // Aquí puedes agregar la lógica para aplicar a la vacante
    if (this.job) {
      alert(`¡Gracias por aplicar a la vacante: ${this.job.position} en ${this.job.company}!`);
      // Puedes agregar más lógica aquí, como enviar una solicitud al servidor, etc.
  
      // Desactivar el botón después de aplicar
      this.disableApplyButton = true;
    }
  }

}
