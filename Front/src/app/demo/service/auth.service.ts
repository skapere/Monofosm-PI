import { Injectable } from '@angular/core';
import { jwtDecode } from 'jwt-decode';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private _username: string | null = null;
  private _email: string | null = null;
  private _role: string | null = null;

  constructor() {
    this.loadUserFromToken();
  }

  fastload(){
    this.loadUserFromToken();
  }

  private loadUserFromToken() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (token) {
      const decodedToken: any = jwtDecode(token);
      this._username = decodedToken.username;
      this._email = decodedToken.email;
      this._role = decodedToken.role;
    }
  }

  get username(): string | null {
    return this._username;
  }get email(): string | null {
    return this._email;
  }get role(): string | null {
    return this._role;
  }

  logout() {
    localStorage.removeItem('access_token');
    sessionStorage.removeItem('access_token');
    this._username = null;
    this._email = null;
    this._role = null;
  }

}
