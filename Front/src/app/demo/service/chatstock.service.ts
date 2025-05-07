import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {map, Observable} from 'rxjs';
import { environment } from 'src/environments/environment';


@Injectable({
  providedIn: 'root'
})
export class ChatStockService {

  private baseUrl: string = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getStocks(): Observable<{ label: string, value: number }[]> {
    return this.http.get<{ stock_exchanges: string[] }>(`${environment.apiUrl}/api/stock_exchanges`).pipe(
      map(response => {
        return response.stock_exchanges.map((stock, index) => ({
          label: stock,
          value: index
        }));
      })
    );
  }

  getAnomalies(stock: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/stock/anomalies`, {
      headers: this.getHeaders(),
      params: { stock }
    });
  }

  getPerformance(stock: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/stock/performance`, {
      headers: this.getHeaders(),
      params: { stock }
    });
  }

  getForecast(stock: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/stock/forecast`, {
      headers: this.getHeaders(),
      params: { stock }
    });
  }

  getRisk(stock: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/stock/risk`, {
      headers: this.getHeaders(),
      params: { stock }
    });
  }

  getChatbotResponse(prompt: string): Observable<any> {
    const context = `You are a Smart Stock Decision Assistant (Chatbot) for the Financial Director of Monoprix, using the MonoFOSM APP. Respond clearly and concisely using financial insight when needed.`;
    const fullPrompt = `${context}\n\nUser: ${prompt}\nAssistant:`;

    return this.http.post(`${this.baseUrl}/stock/chatbot`, { prompt: fullPrompt }, {
      headers: this.getHeaders()
    });
  }



}
