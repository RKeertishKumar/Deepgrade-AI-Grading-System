import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AnalyzerComponent } from './analyzer/analyzer.component';
import { ResponsePageComponent } from './response-page/response-page.component';

const routes: Routes = [
  { path: '', component: AnalyzerComponent },
  { path: 'response-page', component: ResponsePageComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
