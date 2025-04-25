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
  // State management
  loading = false;
  processingState: 'idle' | 'reading' | 'analyzing' | 'complete' | 'error' = 'idle';
  responseText = '';
  fileSelected: File | null = null;
  imageUrl: string | null = null;
  errorMessage: string | null = null;
  userQuestion: string = '';
  
  // Response handling
  responseChunks: string[] = [];
  partialJsonBuffer: string = '';
  responseMetadata: any = {};
  
  // Analytics
  analysisStartTime: number = 0;
  chunkCount: number = 0;
  totalBytesProcessed: number = 0;

  constructor(
    private ollamaService: OllamaService,
    private router: Router, 
    private ngxService: NgxUiLoaderService
  ) {}

  onFileSelected(event: any) {
    this.resetState();
    const file = event.target.files[0];
    
    if (!file) {
      this.setError('No file selected');
      return;
    }

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      this.setError('Invalid file type. Please upload an image (JPEG, PNG, GIF, WEBP)');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      this.setError('File too large. Maximum size is 10MB');
      return;
    }

    this.fileSelected = file;
    this.processingState = 'reading';

    const reader = new FileReader();
    reader.onloadstart = () => this.ngxService.start();
    reader.onload = () => {
      this.imageUrl = reader.result as string;
      this.processingState = 'idle';
      this.ngxService.stop();
    };
    reader.onerror = () => {
      this.setError('Error reading file');
      this.ngxService.stop();
    };
    reader.readAsDataURL(file);
  }

  removeImage() {
    this.resetState();
  }

  analyzeImage() {
    if (!this.fileSelected) {
      this.setError('No image selected for analysis');
      return;
    }

    if (!this.userQuestion.trim()) {
      this.setError('Please enter a question or prompt');
      return;
    }

    this.resetAnalysisState();
    this.processingState = 'analyzing';
    this.analysisStartTime = Date.now();
    this.loading = true;
    this.ngxService.start();

    const reader = new FileReader();
    reader.onload = () => {
      const base64Image = this.extractBase64(reader.result as string);
      
      if (!base64Image) {
        this.setError('Invalid image format');
        return;
      }

      this.ollamaService.analyzeImage(base64Image, this.userQuestion).subscribe({
        next: (chunk: string) => this.handleStreamingResponse(chunk),
        error: (error) => this.handleApiError(error),
        complete: () => this.handleAnalysisComplete()
      });
    };
    reader.onerror = () => this.setError('Error reading image file');
    reader.readAsDataURL(this.fileSelected);
  }

  private extractBase64(dataURL: string): string | null {
    try {
      const parts = dataURL.split(',');
      if (parts.length < 2) return null;
      return parts[1].trim();
    } catch (error) {
      console.error('Base64 extraction error:', error);
      return null;
    }
  }

  private handleStreamingResponse(chunk: string) {
    this.totalBytesProcessed += chunk.length;
    this.chunkCount++;
    
    try {
      // Handle potential partial JSON or multiple JSON objects in one chunk
      this.partialJsonBuffer += chunk;
      
      // Process complete JSON objects from the buffer
      while (this.partialJsonBuffer.includes('\n')) {
        const newlineIndex = this.partialJsonBuffer.indexOf('\n');
        const jsonString = this.partialJsonBuffer.substring(0, newlineIndex).trim();
        this.partialJsonBuffer = this.partialJsonBuffer.substring(newlineIndex + 1);
        
        if (jsonString) {
          this.processJsonChunk(jsonString);
        }
      }
      
      // Handle any remaining partial JSON
      if (this.partialJsonBuffer.trim()) {
        try {
          // Try to parse in case we got a complete JSON without newline
          const jsonResponse = JSON.parse(this.partialJsonBuffer);
          this.processJsonResponse(jsonResponse);
          this.partialJsonBuffer = '';
        } catch (e) {
          // Partial JSON remains in buffer for next chunk
        }
      }
    } catch (error) {
      console.error('Stream processing error:', error);
      this.setError('Error processing streaming response');
    }
  }

  private processJsonChunk(jsonString: string) {
    try {
      const jsonResponse = JSON.parse(jsonString);
      this.processJsonResponse(jsonResponse);
    } catch (error) {
      console.error('JSON parsing error:', error, 'for chunk:', jsonString);
      // Attempt to recover from malformed JSON
      const recoveredContent = this.extractContentFromMalformedJson(jsonString);
      if (recoveredContent) {
        this.responseChunks.push(recoveredContent);
        this.responseText = this.responseChunks.join('');
      }
    }
  }

  private extractContentFromMalformedJson(jsonString: string): string | null {
    // Simple recovery attempt for common malformed JSON patterns
    const contentMatch = jsonString.match(/"content"\s*:\s*"([^"]*)"/);
    return contentMatch ? contentMatch[1] : null;
  }

  private processJsonResponse(jsonResponse: any) {
    // Extract and store metadata if present
    if (jsonResponse.metadata) {
      this.responseMetadata = { ...this.responseMetadata, ...jsonResponse.metadata };
    }

    // Process message content
    if (jsonResponse.message?.content) {
      const content = jsonResponse.message.content;
      this.responseChunks.push(content);
      this.responseText = this.responseChunks.join('');
      
      // Optional: Update UI progressively
      // this.updateProgressiveDisplay();
    }

    // Handle other response types (e.g., errors)
    if (jsonResponse.error) {
      this.setError(jsonResponse.error);
    }
  }

  private handleAnalysisComplete() {
    this.processingState = 'complete';
    this.loading = false;
    this.ngxService.stop();
    
    // Calculate analysis duration
    const duration = (Date.now() - this.analysisStartTime) / 1000;
    console.log(`Analysis completed in ${duration.toFixed(2)} seconds`);
    console.log(`Processed ${this.chunkCount} chunks, ${this.totalBytesProcessed} bytes`);
    
    // Navigate with the complete response
    if (this.responseText) {
      this.router.navigate(['/response-page'], {
        queryParams: {
          response: this.responseText,
          metadata: JSON.stringify({
            duration,
            chunkCount: this.chunkCount,
            ...this.responseMetadata
          })
        }
      });
    } else {
      this.setError('No valid response received from the API');
    }
  }

  private handleApiError(error: any) {
    this.processingState = 'error';
    this.loading = false;
    this.ngxService.stop();
    
    console.error('API Error:', error);
    
    let errorMessage = 'Error analyzing image';
    if (error.status === 0) {
      errorMessage += ' - Network error';
    } else if (error.error?.message) {
      errorMessage += `: ${error.error.message}`;
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    
    this.setError(errorMessage);
  }

  private resetState() {
    this.fileSelected = null;
    this.imageUrl = null;
    this.responseText = '';
    this.errorMessage = null;
    this.userQuestion = '';
    this.processingState = 'idle';
    this.resetAnalysisState();
  }

  private resetAnalysisState() {
    this.responseChunks = [];
    this.partialJsonBuffer = '';
    this.responseMetadata = {};
    this.chunkCount = 0;
    this.totalBytesProcessed = 0;
    this.analysisStartTime = 0;
  }

  private setError(message: string) {
    this.errorMessage = message;
    this.processingState = 'error';
    this.loading = false;
    this.ngxService.stop();
    setTimeout(() => this.errorMessage = null, 5000);
  }

  // Optional: For progressive display of chunks
  private updateProgressiveDisplay() {
    // This could update a UI element progressively as chunks arrive
    // For example, using ViewChild to update a specific element
    // Or emitting an event to a parent component
  }
}