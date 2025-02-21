import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { NgxUiLoaderService } from 'ngx-ui-loader';

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

  constructor(private http: HttpClient, private router: Router, private ngxService: NgxUiLoaderService) {}

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
      this.ngxService.start(); // Show loader

      const reader = new FileReader();
      reader.onload = () => {
        const base64Image = reader.result?.toString().split(',')[1]?.trim();

        if (base64Image) {
          this.sendToOllama(base64Image);
        } else {
          this.loading = false;
          this.ngxService.stop(); // Hide loader
          this.errorMessage = 'Failed to read image!';
        }
      };
      reader.readAsDataURL(this.fileSelected);
    }
  }

  sendToOllama(base64Image: string) {
    const requestBody = {
      model: 'llama3.2-vision',
      messages: [
        {
          role: 'user',
          content: 'Analyze this image',
          images: [base64Image]
        }
      ]
    };

    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    this.http.post('http://localhost:11434/api/chat', requestBody, { headers, responseType: 'text' }).subscribe(
      (responseText: string) => {
        this.loading = false;
        this.ngxService.stop(); // Hide loader

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

          // Debugging: Log the final response and navigation attempt
          console.log('Final Response:', finalResponse);
          console.log('Navigating to /response-page...');

          // Navigate to the response page with the response data
          this.router.navigate(['/response-page'], { queryParams: { response: finalResponse } });
        } catch (error) {
          console.error('Error processing API response:', error);
          this.responseText = 'Error processing API response!';
        }
      },
      (error) => {
        this.loading = false;
        this.ngxService.stop(); // Hide loader
        console.error('Ollama API Error:', error);
        this.errorMessage = 'Error analyzing image!';
      }
    );
  }
}