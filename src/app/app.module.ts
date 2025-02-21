import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AnalyzerComponent } from './analyzer/analyzer.component';
import { HttpClientModule } from '@angular/common/http';
import { NZ_I18N } from 'ng-zorro-antd/i18n';
import { en_US } from 'ng-zorro-antd/i18n';
import { registerLocaleData } from '@angular/common';
import en from '@angular/common/locales/en';
import { FormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

// Import necessary ng-zorro modules
import { NzButtonModule } from 'ng-zorro-antd/button'; // For Ant Design buttons
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NgxUiLoaderModule, NgxUiLoaderConfig, SPINNER } from 'ngx-ui-loader'; // Importing NgxUiLoaderModule and SPINNER

import { ResponsePageComponent } from './response-page/response-page.component'; // For Ant Design icons

registerLocaleData(en);

const ngxUiLoaderConfig: NgxUiLoaderConfig = {
  fgsType: SPINNER.ballSpinClockwise, // Type of spinner
  fgsColor: '#7054FF', // Spinner color
  pbColor: '#7054FF', // Progress bar color
  bgsOpacity: 0.5, // Background opacity
  overlayColor: 'rgba(8, 11, 35, 0.8)', // Overlay color
  hasProgressBar: false, // Show/hide progress bar
};

@NgModule({
  declarations: [
    AppComponent,
    AnalyzerComponent,
    ResponsePageComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    BrowserAnimationsModule,  // Required for animations in ng-zorro
    NzButtonModule,           // Import for buttons
    NzIconModule,             // Import for icons
    NgxUiLoaderModule.forRoot(ngxUiLoaderConfig), // Importing and configuring NgxUiLoaderModule
  ],
  providers: [
    { provide: NZ_I18N, useValue: en_US },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
