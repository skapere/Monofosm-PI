import { Component, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';

@Component({
  selector: 'app-dashboardpowerbi',
  templateUrl: './dashboardpowerbi.component.html',
  styles: [`
    .powerbi-container {
      width: 100%;
      height: 90vh; /* Adjust height as needed */
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .powerbi-container iframe {
      border: none;
      width: 100%;
      height: 100%;
    }
  `]
})
export class DashboardpowerbiComponent implements OnInit, AfterViewInit {

  @ViewChild('powerbiContainer', { static: true }) powerbiContainer!: ElementRef;

  constructor() {}

  ngOnInit() {}

  ngAfterViewInit() {
    };

}
