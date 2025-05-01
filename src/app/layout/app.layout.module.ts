import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { InputTextModule } from 'primeng/inputtext';
import { SidebarModule } from 'primeng/sidebar';
import { BadgeModule } from 'primeng/badge';
import { RadioButtonModule } from 'primeng/radiobutton';
import { InputSwitchModule } from 'primeng/inputswitch';
import { RippleModule } from 'primeng/ripple';
import { AppMenuComponent } from './app.menu.component';
import { AppMenuitemComponent } from './app.menuitem.component';
import { RouterModule } from '@angular/router';
import { AppTopBarComponent } from './app.topbar.component';
import { AppFooterComponent } from './app.footer.component';
import { AppConfigModule } from './config/config.module';
import { AppSidebarComponent } from "./app.sidebar.component";
import { AppLayoutComponent } from "./app.layout.component";
import {SpeedDialModule} from "primeng/speeddial";
import {ToastModule} from "primeng/toast";
import {MenubarModule} from "primeng/menubar";
import {DialogModule} from "primeng/dialog";
import {DividerModule} from "primeng/divider";
import {PasswordModule} from "primeng/password";
import {MessagesModule} from "primeng/messages";
import {ScrollTopModule} from "primeng/scrolltop";
import {ScrollPanelModule} from "primeng/scrollpanel";
import {TableModule} from "primeng/table";
import {ChipModule} from "primeng/chip";
import {DropdownModule} from "primeng/dropdown";
import {CheckboxModule} from "primeng/checkbox";

@NgModule({
    declarations: [
        AppMenuitemComponent,
        AppTopBarComponent,
        AppFooterComponent,
        AppMenuComponent,
        AppSidebarComponent,
        AppLayoutComponent,
    ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    BrowserAnimationsModule,
    InputTextModule,
    SidebarModule,
    BadgeModule,
    RadioButtonModule,
    InputSwitchModule,
    RippleModule,
    RouterModule,
    AppConfigModule,
    SpeedDialModule,
    ToastModule,
    MenubarModule,
    DialogModule,
    DividerModule,
    PasswordModule,
    MessagesModule,
    ScrollTopModule,
    ScrollPanelModule,
    TableModule,
    ChipModule,
    DropdownModule,
    CheckboxModule
  ],
    exports: [AppLayoutComponent]
})
export class AppLayoutModule { }
