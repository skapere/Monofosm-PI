import { NgModule } from '@angular/core';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { AppLayoutModule } from './layout/app.layout.module';
import { NotfoundComponent } from './demo/components/notfound/notfound.component';
import {UserService} from "./demo/service/user.service";
import {TokenInterceptor} from "./demo/service/token.interceptor";
import { CommonModule } from '@angular/common';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { ToggleButtonModule } from 'primeng/togglebutton';
import { RippleModule } from 'primeng/ripple';
import { MultiSelectModule } from 'primeng/multiselect';
import { DropdownModule } from 'primeng/dropdown';
import { ProgressBarModule } from 'primeng/progressbar';
import { ToastModule } from 'primeng/toast';
import { SliderModule } from 'primeng/slider';
import { RatingModule } from 'primeng/rating';
import { FormsModule } from '@angular/forms';
import {AuthGuard} from "./demo/service/auth.guard";
import {AuthService} from "./demo/service/auth.service";
import {DialogModule} from "primeng/dialog";
import {FileUploadModule} from "primeng/fileupload";
import {InputNumberModule} from "primeng/inputnumber";
import {InputTextareaModule} from "primeng/inputtextarea";
import {RadioButtonModule} from "primeng/radiobutton";
import {ToolbarModule} from "primeng/toolbar";
import {TagModule} from "primeng/tag";
import {OverlayPanelModule} from "primeng/overlaypanel";
import {MessageService} from "primeng/api";
import {ChatStockService} from "./demo/service/chatstock.service";
import {supplierService} from "./demo/service/supplier.service";
import {SalesService} from "./demo/service/sales.service";
import {DashboardpowerbiComponent} from "./demo/components/dashboardPowerBI/dashboardpowerbi.component";

@NgModule({
    declarations: [
        AppComponent, NotfoundComponent , DashboardpowerbiComponent
    ],
  imports: [
    AppRoutingModule,
    AppLayoutModule,
    TableModule,
    CommonModule,
    RatingModule,
    ButtonModule,
    SliderModule,
    InputTextModule,
    ToggleButtonModule,
    RippleModule,
    MultiSelectModule,
    DropdownModule,
    ProgressBarModule,
    ToastModule,
    FormsModule,
    DialogModule,
    FileUploadModule,
    InputNumberModule,
    InputTextareaModule,
    RadioButtonModule,
    ToolbarModule,
    TagModule,
    OverlayPanelModule
  ],
    providers: [
        { provide: LocationStrategy, useClass: HashLocationStrategy },
        UserService, TokenInterceptor, AuthGuard, AuthService, MessageService, ChatStockService, supplierService, SalesService
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
