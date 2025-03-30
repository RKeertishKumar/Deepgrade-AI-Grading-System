import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { NgxUiLoaderService } from 'ngx-ui-loader';
import { OllamaService } from '../../services/ollama.service';

@Component({
  selector: 'app-analyzer',
  templateUrl: './analyzer.component.html',
  styleUrls: ['./analyzer.component.scss']
})
export class AnalyzerComponent {
  loading = false;
  responseText = '';
  fileSelected: File | null = null;
  imageUrl: string | null = null;
  errorMessage: string | null = null;

  constructor(
    private ollamaService: OllamaService,
    private router: Router, 
    private ngxService: NgxUiLoaderService
  ) {}

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.fileSelected = file;

      const reader = new FileReader();
      reader.onload = () => {
        this.imageUrl = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  removeImage() {
    this.fileSelected = null;
    this.imageUrl = null;
    this.responseText = '';
  }

  analyzeImage() {
    if (this.fileSelected) {
      this.loading = true;
      this.responseText = '';
      this.ngxService.start();

      const reader = new FileReader();
      reader.onload = () => {
        const base64Image = reader.result?.toString().split(',')[1]?.trim();

        if (base64Image) {
          this.ollamaService.analyzeImage(base64Image).subscribe({
            next: (responseText: string) => this.handleApiResponse(responseText),
            error: (error) => this.handleApiError(error)
          });
        } else {
          this.handleImageReadError();
        }
      };
      reader.readAsDataURL(this.fileSelected);
    }
  }

  private handleApiResponse(responseText: string) {
    this.loading = false;
    this.ngxService.stop();

    try {
      console.log('Raw Response:', responseText);
      const jsonObjects = responseText.split('\n').filter(line => line.trim() !== '');
      let finalResponse = '';

      for (const jsonString of jsonObjects) {
        try {
          const jsonResponse = JSON.parse(jsonString);
          if (jsonResponse.message && jsonResponse.message.content) {
            finalResponse += jsonResponse.message.content;
          }
        } catch (error) {
          console.error('Error parsing JSON chunk:', error);
        }
      }

      this.responseText = finalResponse;
      console.log('Final Response:', finalResponse);
      console.log('Navigating to /response-page...');

      this.router.navigate(['/response-page'], { 
        queryParams: { response: finalResponse } 
      });
    } catch (error) {
      console.error('Error processing API response:', error);
      this.responseText = 'Error processing API response!';
    }
  }

  private handleApiError(error: any) {
    this.loading = false;
    this.ngxService.stop();
    console.error('Ollama API Error:', error);
    this.errorMessage = 'Error analyzing image!';
  }

  private handleImageReadError() {
    this.loading = false;
    this.ngxService.stop();
    this.errorMessage = 'Failed to read image!';
  }
}