import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (!token) {
      this.router.navigate(['/auth/login']);
      return false;
    }

    const expectedRoles = route.data['expectedRoles'];
    if (expectedRoles && expectedRoles.length > 0) {
      const userRole = this.authService.role;
      if (!expectedRoles.includes(userRole)) {
        this.router.navigate(['/auth/login']);
        return false;
      }
    }

    return true;
  }
}
