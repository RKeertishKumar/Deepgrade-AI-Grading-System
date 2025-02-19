import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AnalyzerComponent } from './analyzer/analyzer.component';

const routes: Routes = [
  { path: 'analyze-page', component: AnalyzerComponent },
  { path: '', redirectTo: '/analyze-page', pathMatch: 'full' }, 
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
