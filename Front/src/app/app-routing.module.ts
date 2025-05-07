import { RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';
import { NotfoundComponent } from './demo/components/notfound/notfound.component';
import { AppLayoutComponent } from "./layout/app.layout.component";
import { AuthGuard } from './demo/service/auth.guard';
import {DashboardpowerbiComponent} from "./demo/components/dashboardPowerBI/dashboardpowerbi.component";

@NgModule({
  imports: [
    RouterModule.forRoot([
      {
        path: 'MonoFOSM', component: AppLayoutComponent,
        children: [
          { path: 'dashboard', component: DashboardpowerbiComponent},
        ],
      },
      { path: 'auth', loadChildren: () => import('./demo/components/auth/auth.module').then(m => m.AuthModule) },
      { path: '', loadChildren: () => import('./demo/components/landing/landing.module').then(m => m.LandingModule) },
      { path: 'notfound', component: NotfoundComponent },
      { path: '**', redirectTo: 'notfound' },
    ], { scrollPositionRestoration: 'enabled', anchorScrolling: 'enabled', onSameUrlNavigation: 'reload' })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule { }
