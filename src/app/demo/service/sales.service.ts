import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {map, Observable} from 'rxjs';
import { environment } from 'src/environments/environment';


@Injectable({
  providedIn: 'root'
})
export class SalesService {

  private baseUrl: string = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }



  getProductRecommendations(n: number = 5): Observable<any> {
    return this.http.get(`${this.baseUrl}/recommend_product_pairs`, {
      headers: this.getHeaders(),
      params: {
        n
      }
    });
  }

  //Region Store Layout


  generateLayoutTemplate(params: any): Observable<any> {
    return this.http.get(`http://localhost:5000/api/generate_layout_template`, { params });
  }

  optimizeLayout(payload: any): Observable<any> {
    return this.http.post(`http://localhost:5000/api/optimize_layout`, payload);
  }

  categoryRecom(payload: any): Observable<any> {
    return this.http.post(`http://localhost:5000/api/recommend_category_placement`, payload);
  }



  //End Store layout





}
