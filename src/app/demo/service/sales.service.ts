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


  generateLayoutTemplate(endpoint: string, params: any): Observable<any> {
    return this.http.get(`http://localhost:5000/api/${endpoint}`, { params });
  }

  optimizeLayout(endpoint: string, payload: any): Observable<any> {
    return this.http.post(`http://localhost:5000/api/${endpoint}`, payload);
  }



  //End Store layout


  /*
  generateStoreLayout(
    shape: string,
    width: number,
    height: number,
    includeButcher = true,
    includeFruitsVegetables = true,
    includeSpices = true,
    includeStaffRoom = true
  ): Observable<any> {
    const body = {
      shape,
      width,
      height,
      include_butcher: includeButcher,
      include_fruits_vegetables: includeFruitsVegetables,
      include_spices: includeSpices,
      include_staff_room: includeStaffRoom
    };
    return this.http.post(`${this.baseUrl}/generate_store_layout`, body, {
      headers: this.getHeaders()
    });
  }


  arrangeProducts(layout: string[][]): Observable<any> {
    const body = { layout };
    return this.http.post(`${this.baseUrl}/arrange_products`, body, {
      headers: this.getHeaders()
    });
  }
*/




}
