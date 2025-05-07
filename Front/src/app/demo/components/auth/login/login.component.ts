import { Component } from '@angular/core';
import { LayoutService } from 'src/app/layout/service/app.layout.service';
import { UserService } from 'src/app/demo/service/user.service';
import { HttpClient } from "@angular/common/http";
import { NgForm } from "@angular/forms";
import { Router } from '@angular/router';
import {AuthService} from "../../../service/auth.service";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styles: [`
    :host ::ng-deep .p-password input {
      width: 100%;
      padding:1rem;
    }

    :host ::ng-deep .pi-eye {
      transform:scale(1.6);
      margin-right: 1rem;
      color: var(--primary-color) !important;
    }

    :host ::ng-deep .pi-eye-slash {
      transform:scale(1.6);
      margin-right: 1rem;
      color: var(--primary-color) !important;
    }
  `]
})
export class LoginComponent {
  valCheck: string[] = ['remember'];
  email: string = '';
  password: string = '';
  rememberMe: boolean = false; // Add a property for the "Remember Me" checkbox
  errorMessage: string = '';


  constructor(private userService: UserService, public layoutService: LayoutService, private router: Router, private authService: AuthService) { }

  /*onLoginClick() {
    this.userService.getAllUsers().subscribe(
      (response) => {
        // Handle successful login
        console.log('Login successful:', response);
      },
      (error) => {
        // Handle error
        console.error('Login failed:', error);
        this.errorMessage = 'Invalid login credentials'; // Display an error message
      }
    );
  }*/
  onLoginClick() {
    this.userService.login(this.email, this.password).subscribe(
      (response) => {
        if (response.success && response.access_token) {
          console.log('Login successful');

          // Stocker le token selon l'option choisie
          if (this.rememberMe) {
            localStorage.setItem('access_token', response.access_token);
          } else {
            sessionStorage.setItem('access_token', response.access_token);
          }

          // Charger l'utilisateur
          this.authService.fastload();

          // Rediriger vers une page sécurisée
          this.router.navigateByUrl('/MonoFOSM/dashboard');

          // Réinitialiser le message d'erreur
          this.errorMessage = '';
        } else {
          this.errorMessage = response.message || 'Identifiants invalides';
        }
      },
      (error) => {
        if (error.status === 401) {
          this.errorMessage = 'Email ou mot de passe invalide';
        } else {
          this.errorMessage = 'Une erreur est survenue. Veuillez réessayer.';
        }
      }
    );
  }




}
