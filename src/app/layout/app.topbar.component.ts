import {Component, ElementRef, ViewChild} from '@angular/core';
import {MenuItem, Message, MessageService} from 'primeng/api';
import {LayoutService} from "./service/app.layout.service";
import {AuthService} from '../demo/service/auth.service';
import {Router} from '@angular/router';
import {UserService} from "../demo/service/user.service";
import {Cell} from "../demo/api/cell.model";
import {ChatStockService} from "../demo/service/chatstock.service";
import {supplierService} from "../demo/service/supplier.service";
import {SalesService} from "../demo/service/sales.service";
import {Reponse} from "../demo/api/Recipe.model";
import {Observable} from "rxjs";

@Component({
  selector: 'app-topbar',
  templateUrl: './app.topbar.component.html',
  providers: [MessageService]
})
export class AppTopBarComponent {

  selectedOption: string | null = "chatbot";

  choseOptions = [
    { label: 'ChatBot', value: "chatbot" },
    { label: 'Anomalies', value: "anomal" },
    { label: 'Performance', value: "performance" },
    { label: 'Predict', value: "predict" }
  ];
  selectedstock: number | null = null;
  pairsnumber: number | null = null;
  selectedCategory: string | null = null;

  stockOptions: { label: string, value: number }[] = [];
  CategoryOptions: { label: string, value: string }[] = [];
  items!: MenuItem[];

  tieredItems!: MenuItem[];
  userName: string | null = '';
  email: string | null = '';
  role: string | null = '';
  visible: boolean = false;
  chatbotReponces: { question: string, response: string }[] = [];
  question: string = '';
  chatbotdialog: boolean = false;
  SupplierRecommendationdialog: boolean = false;
  SalesRecommendationdialog: boolean = false;
  passwordValue: string ='';
  ConfirmPasswordValue: string ='';
  isPasswordMatch: boolean = true;
  messageserror: Message[] = [{ severity: 'error', detail: 'Passwords do not match!' }];
  supplierRecommendations: any[] = [];
  SalesRecommendations: any[] = [];

  /*storeLayout: string[][] = [];
  arrangedProducts: any[] = [];
  layoutShape: string = 'rectangle';
  layoutWidth: number = 5;
  layoutHeight: number = 5;
  loadingLayout = false;
  loadingArrangement = false;
  includeButcher = false;
  includeFruitsVegetables = false;
  includeSpices = false;
  includeStaffRoom = false;

  doorPosition: number[] | null = null;
  cashierPositions: number[][] = [];
  staffRoomPosition: number[] | null = null;
  butcherPosition: number[] | null = null;
  fruitsVegetablesPosition: number[] | null = null;
  spicesPosition: number[] | null = null;

  selectedCellType = 'Aisle';
  cellTypes = [
    { label: 'Walkway', value: 'Walkway' },
    { label: 'Aisle', value: 'Aisle' },
    { label: 'Cashier', value: 'Cashier' },
    { label: 'Door', value: 'Door' },
    { label: 'Staff Room', value: 'StaffRoom' },
    { label: 'Butcher', value: 'Butcher' },
    { label: 'Fruits & Veg', value: 'FruitsVeg' },
    { label: 'Spices', value: 'Spices' },
  ];*/


  // Region Store layout

  StoreLayoutDialog: boolean = false;

  storeWidth: number = 10;
  storeHeight: number = 10;
  cellSize: number = 1;

  layout: Cell[][] = [];
  loadingLayout: boolean = false;

  selectedZoneType: string = 'Empty'; // default selected zone

  zoneTypes: string[] = [
    'Empty', 'Walkway', 'Door'
  ];

  //End Store layout


  loading: boolean = false;
  loadingSupplier: boolean = false;
  loadingSales: boolean = false;





  @ViewChild('menubutton') menuButton!: ElementRef;

  @ViewChild('topbarmenubutton') topbarMenuButton!: ElementRef;

  @ViewChild('topbarmenu') menu!: ElementRef;


  constructor(public layoutService: LayoutService, private authService: AuthService, private router: Router, private salesService: SalesService, private supplierService: supplierService, private ChatStockService: ChatStockService){}

  ngOnInit() {
    this.authService.fastload();
    this.userName = this.authService.username;
    this.email = this.authService.email;
    this.role = this.authService.role;

    if(this.role == 'Finance')
    {
      this.ChatStockService.getStocks().subscribe(stockOptions => {
        this.stockOptions = stockOptions;
      });
    }
    if(this.role == 'Supplier Management')
    {
      this.supplierService.getCategories().subscribe(categoryOptions => {
        this.CategoryOptions = categoryOptions;
        this.selectedCategory = categoryOptions[0].value;
        this.submitSupplierRecommendation();
      });
    }
    if(this.role == 'Sales')
    {
      this.pairsnumber = 5;
      this.submitSalesRecommendation();
    }

    this.loadUsername();
  }
  arePasswordsMatching(): boolean {
    this.isPasswordMatch = this.passwordValue === this.ConfirmPasswordValue;
    if(!this.isPasswordMatch)
    {
      this.messageserror = [{ severity: 'error', detail: 'Passwords do not match!' }];
    }
    return this.isPasswordMatch;
  }
  getRoleClass(role: string | null): string {
    if(role)
    {
      if (role === 'Finance') {
        return 'qualified';
      } else if (role === 'Supplier Management') {
        return 'proposal';
      } else if (role === 'Sales') {
        return 'renewal';
      } else {
        return 'unqualified';
      }
    }
    else {
      return 'new';
    }
  }
  loadUsername() {
    this.tieredItems = [
      {
        label: this.userName ? this.userName : 'LogIn',
        icon: 'pi pi-fw pi-user',
        items: this.userName ? [
          {
            label: 'My profile',
            icon: 'pi pi-fw pi-file',
            command: () => this.showDialog()
          },
          {
            label: 'LogOut',
            icon: 'pi pi-fw pi-sign-out',
            command: () => this.logout() // LogOut
          }
        ] :[
          {
            label: 'LogIn',
            icon: 'pi pi-fw pi-sign-in',
            command: () => this.router.navigate(['/auth/login'])
          },
        ]
      },
      { separator: true },
    ];
  }
  logout() {
    this.authService.logout();
    this.userName = null;
    this.ngOnInit();
    this.router.navigate(['/auth/login']);
  }
  showDialog() {
    this.visible = true;
  }
  showChatBotDialog() {
    this.chatbotdialog = this.role == 'Finance';
    this.SupplierRecommendationdialog = this.role == 'Supplier Management';
    this.SalesRecommendationdialog = this.role == 'Sales';

  }
  submitSalesRecommendation() {
    if (this.loadingSales || !this.pairsnumber) return;


    this.loadingSales = true;
    this.salesService.getProductRecommendations(this.pairsnumber).subscribe({
      next: (data) => {
        this.SalesRecommendations = data.top_product_pairs || []; // Adjust based on your API response shape
        this.loadingSales = false;

      },
      error: (err) => {
        console.error('Failed to load product pairs recommendation', err);
        this.SalesRecommendations = [{
          product1_name: 'Error loading data',
          product2_name: '-',
          score: '-'
        }];
        this.loadingSales = false;
      }
    });
  }

  submitSupplierRecommendation() {
    if (this.loadingSupplier || !this.selectedCategory) return;
    this.loadingSupplier = true;
    const selectedCategoryLabel = this.CategoryOptions.find(c => c.value === this.selectedCategory)?.label;

    this.supplierService.getSupplierRecommendations(selectedCategoryLabel!)
      .subscribe({
        next: (data) => {
          this.supplierRecommendations = data.recommendations;
          this.loadingSupplier = false;
        },
        error: (err) => {
          console.error('Failed to load recommendations', err);
          this.supplierRecommendations = [{
            SupplierName: 'Error loading data',
            Country: '-',
            AvgSupplierPrice: '-',
            HasDisputes: '-',
            NumberOfTransactions: '-'
          }];
          this.loadingSupplier = false;
        }
      });
  }
  private prepareUserQuestion(): string | null {
    if (this.selectedOption === 'chatbot') {
      return this.question.trim() ? this.question : null;
    }

    const selectedStockLabel = this.stockOptions.find(s => s.value === this.selectedstock)?.label;
    if (!this.selectedOption || !selectedStockLabel) return null;

    switch (this.selectedOption) {
      case 'anomal':
        this.question = `What are the anomalies for ${selectedStockLabel}?`;
        break;
      case 'performance':
        this.question = `What is the performance of ${selectedStockLabel}?`;
        break;
      case 'predict':
        this.question = `What is the forecast for ${selectedStockLabel}?`;
        break;
      case 'risk':
        this.question = `What is the risk for ${selectedStockLabel}?`;
        break;
    }

    return this.question;
  }
  private getObservable(userQuestion: string): Observable<any> {
    const selectedStockLabel = this.stockOptions.find(s => s.value === this.selectedstock)?.label;

    switch (this.selectedOption) {
      case 'chatbot':
        return this.ChatStockService.getChatbotResponse(userQuestion);
      case 'anomal':
        return this.ChatStockService.getAnomalies(selectedStockLabel!);
      case 'performance':
        return this.ChatStockService.getPerformance(selectedStockLabel!);
      case 'predict':
        return this.ChatStockService.getForecast(selectedStockLabel!);
      case 'risk':
        return this.ChatStockService.getRisk(selectedStockLabel!);
      default:
        throw new Error('Invalid option selected');
    }
  }
  private formatAnomalies(anomalies: any[]): string {
    if (!anomalies?.length) return "No anomalies detected for this stock.";

    return anomalies.map((a, i) =>
      `Anomaly ${i + 1}:\n- Date: ${new Date(a.SEDate.$date).toLocaleDateString()}\n- Price: ${a.LastPrice.toFixed(4)}\n- Volume: ${a.TradingVolume.toFixed(4)}\n- Reason: ${a.Reason}`
    ).join('\n\n');
  }
  private handleResponse(data: any, userQuestion: string): void {
    let botReply = '';

    switch (this.selectedOption) {
      case 'chatbot':
        botReply = data.response;
        break;
      case 'anomal':
        botReply = this.formatAnomalies(data.anomalies);
        break;
      case 'performance':
        const perf = data.performance;
        botReply = `Stock Performance:\n- Average Return: ${perf.AverageReturn.toFixed(2)}\n- Volatility: ${perf.Volatility.toFixed(2)}\n- Trend: ${perf.Trend}`;
        break;
      case 'predict':
        const forecast = data.forecast;
        botReply = `7-Day Forecast:\n- Predicted Change: ${forecast.PredictedChange.toFixed(2)}%\n- Confidence: ${forecast.Confidence.toFixed(2)}%`;
        break;
      case 'risk':
        botReply = `1-Day Value at Risk (95%): ${data.VaR_1day_95pct.toFixed(2)}`;
        break;
    }

    this.chatbotReponces.push({ question: userQuestion, response: botReply });
    this.question = '';
    this.loading = false;
  }
  private handleError(error: any, userQuestion: string): void {
    console.error('API failed, falling back to chatbot:', error);

    this.ChatStockService.getChatbotResponse(userQuestion).subscribe({
      next: (fallbackData) => {
        this.chatbotReponces.push({
          question: userQuestion,
          response: fallbackData.response
        });
        this.loading = false;
      },
      error: (fallbackError) => {
        console.error('Fallback chatbot also failed:', fallbackError);
        this.chatbotReponces.push({
          question: userQuestion,
          response: "An error occurred. Please try again later."
        });
        this.loading = false;
      }
    });
  }
  submitChat() {
    if (this.loading) return;

    const userQuestion = this.prepareUserQuestion();
    if (!userQuestion) return;

    this.loading = true;
    const observable = this.getObservable(userQuestion);

    observable.subscribe({
      next: (data) => this.handleResponse(data, userQuestion),
      error: (error) => this.handleError(error, userQuestion)
    });
  }

  /*

  generateLayout() {
    this.loadingLayout = true;
    this.salesService.generateStoreLayout(
      this.layoutShape,
      this.layoutWidth,
      this.layoutHeight,
      this.includeButcher,
      this.includeFruitsVegetables,
      this.includeSpices,
      this.includeStaffRoom
    ).subscribe({
      next: (data) => {
        this.storeLayout = data.layout;
        this.doorPosition = data.door_position || null;
        this.cashierPositions = data.cashier_positions || [];
        this.staffRoomPosition = data.staff_room_position || null;
        this.butcherPosition = data.butcher_position || null;
        this.fruitsVegetablesPosition = data.fruits_vegetables_position || null;
        this.spicesPosition = data.spices_position || null;

        this.arrangedProducts = [];
        this.loadingLayout = false;
      },
      error: () => {
        this.loadingLayout = false;
      }
    });
  }


  arrangeProducts() {
    this.loadingArrangement = true;
    this.salesService.arrangeProducts(this.storeLayout).subscribe({
      next: (data) => {
        this.arrangedProducts = data.product_arrangement;
        this.loadingArrangement = false;
      },
      error: () => {
        this.loadingArrangement = false;
      }
    });
  }

  getFormattedCashierPositions(): string {
    return this.cashierPositions
      .map(pos => pos.join(', '))
      .join(' | ');
  }

  debugcheckbox(statue: boolean): void {
    console.log(statue);
  }

  getCellColor(cell: string): string {
    switch (cell) {
      case 'Walkway': return '#f0f0f0';
      case 'Empty': return '#e1e1e1';
      case 'Aisle': return '#8bc34a';
      case 'Cashier': return '#03a9f4';
      case 'Door': return '#ff5722';
      case 'StaffRoom': return '#9c27b0';
      case 'Butcher': return '#795548';
      case 'FruitsVeg': return '#ffc107';
      case 'Spices': return '#ff9800';
      default: return '#e0e0e0';
    }
  }

  getCellEmogie(cell: string): string {
    switch (cell) {
      case 'Empty': return 'Empty';
      case 'Walkway': return 'Walkway';
      case 'Aisle': return 'Aisle';
      case 'Cashier': return '💰 Cashiers';
      case 'Door': return '🚪 Door';
      case 'StaffRoom': return '👥 Staff Room';
      case 'Butcher': return '🥩 Butcher';
      case 'FruitsVeg': return '🍎 Fruits & Veg';
      case 'Spices': return '🧂 Spices';
      default: return '';
    }
  }



  createEmptyLayout() {
    this.storeLayout = Array.from({ length: this.layoutHeight }, () =>
      Array.from({ length: this.layoutWidth }, () => 'Walkway')
    );
  }


  trackByIndex(index: number): number {
    return index;
  }


  onCellClick(row: number, col: number) {
    console.log('Clicked:', row, col, 'Type:', this.selectedCellType);
    const updatedRow = [...this.storeLayout[row]];
    updatedRow[col] = this.selectedCellType;
    this.storeLayout[row] = updatedRow;
    this.storeLayout = [...this.storeLayout];
  }
*/

  //Region Store layout
  openStoreLayoutDialog() {
    this.StoreLayoutDialog = true;
    this.zoneTypes = [
      'Empty', 'Walkway', 'Door'
    ];
  }

  generateLayout(): void {
    this.loadingLayout = true;

    this.zoneTypes = [
      'Empty', 'Walkway', 'Door'
    ];

    const params = {
      width: this.storeWidth,
      height: this.storeHeight,
      cell_size: this.cellSize
    };

    this.salesService.generateLayoutTemplate('generate_layout_template', params).subscribe({
      next: (data) => {
        this.layout = data.grid;
        this.loadingLayout = false;
      },
      error: (error) => {
        console.error('Error generating layout:', error);
        this.loadingLayout = false;
      }
    });

  }

  optimizeStoreLayout(): void {
    const payload = {
      grid: this.layout,
      rows: this.layout.length,
      cols: this.layout[0]?.length || 0,
      cell_size: this.cellSize
    };

    this.zoneTypes = [
      'Empty', 'Walkway', 'Aisle', 'Cashier',
      'Door', 'StaffRoom', 'Butcher', 'FruitsVeg', 'Spices'
    ];

    this.salesService.optimizeLayout('optimize_layout', payload).subscribe({
      next: (data) => {
        this.layout = data.grid;
      },
      error: (error) => {
        console.error('Error optimizing layout:', error);
      }
    });
  }



  getCellColor(row: number,cell: number): string {
    switch (this.layout[row][cell].type) {
      case 'Empty': return '#e1e1e1';
      case 'Walkway': return '#f0f0f0';
      case 'Aisle': return '#8bc34a';
      case 'Cashier': return '#03a9f4';
      case 'Door': return '#ff5722';
      case 'StaffRoom': return '#9c27b0';
      case 'Butcher': return '#795548';
      case 'FruitsVeg': return '#ffc107';
      case 'Spices': return '#ff9800';
      default: return '#e0e0e0';
    }
  }

  getCellEmogie(row: number, cell: number): string {
    switch (this.layout[row][cell].type) {
      case 'Empty': return 'Empty';
      case 'Walkway': return 'Walkway';
      case 'Aisle': return 'Aisle';
      case 'Cashier': return '💰 Cashiers';
      case 'Door': return '🚪 Door';
      case 'StaffRoom': return '👥 Staff Room';
      case 'Butcher': return '🥩 Butcher';
      case 'FruitsVeg': return '🍎 Fruits & Veg';
      case 'Spices': return '🧂 Spices';
      default: return '';
    }
  }

  onCellClick(row: number, col: number): void {
    if (this.layout && this.layout[row] && this.layout[row][col]) {
      this.layout[row][col].type = this.selectedZoneType;
    }
  }






}
