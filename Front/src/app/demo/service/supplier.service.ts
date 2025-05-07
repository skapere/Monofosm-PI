import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {map, Observable} from 'rxjs';
import { environment } from 'src/environments/environment';


@Injectable({
  providedIn: 'root'
})
export class supplierService {

  private baseUrl: string = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getCategories(): Observable<{ label: string, value: string }[]> {
    return this.http.get<{ categories: string[] }>(`${environment.apiUrl}/api/categories`).pipe(
      map(response => {
        return response.categories.map(category => ({
          label: category,
          value: category // use category string as value, not index
        }));
      })
    );
  }


  getSupplierRecommendations(category: string, n: number = 5, preferred_country: string = 'France'): Observable<any> {
    return this.http.get(`${this.baseUrl}/recommend_suppliers`, {
      headers: this.getHeaders(),
      params: {
        category,
        n,
        preferred_country
      }
    });
  }




}
