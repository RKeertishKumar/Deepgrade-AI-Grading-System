import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { GradingService } from '../../services/grading.service';

@Component({
  selector: 'app-response-page',
  templateUrl: './response-page.component.html',
  styleUrls: ['./response-page.component.scss']
})
export class ResponsePageComponent implements OnInit {
  responseText: string = '';
  formattedResponse: SafeHtml = '';
  score: number = 0;
  maxScore: number = 100;
  scoreColor: string = '#7054FF';

  // Enhanced grading criteria with more flexible regex
  gradingCriteria: any[] = [
    { name: 'S1: Start-End Node Check', pattern: /(?:start|beginning).*?(?:end|finish)/i, weight: 20, matched: false },
    { name: 'S2: Unique Sequential Node IDs Check', pattern: /(?:unique|sequential).*?\d+\/\d+/i, weight: 15, matched: false },
    { name: 'S3: Valid Node Types Check', pattern: /(?:start|end|process|decision|action|operation|valid.*type)/i, weight: 15, matched: false },
    { name: 'S4: Connected Nodes Check', pattern: /(?:connected|isolated|linked|disconnected)/i, weight: 15, matched: false },
    { name: 'S5: Decision Node Outgoing Edges Check', pattern: /(?:yes|no).*?outgoing/i, weight: 10, matched: false },
    { name: 'S6: Clear Labels Check', pattern: /(?:clear|meaningful|descriptive).*?label/i, weight: 10, matched: false },
    { name: 'S7: Complete Path from Start to End Check', pattern: /(?:path|sequence).*?(start.*?end|complete.*?path)/i, weight: 15, matched: false }
  ];

  constructor(
    private route: ActivatedRoute,
    private sanitizer: DomSanitizer,
    private gradingService: GradingService
  ) {
    console.log('Component initialized - constructor');
  }

  ngOnInit(): void {
    console.log('ngOnInit triggered');
    
    this.route.queryParams.subscribe(params => {
      console.log('Query params received:', params);
      this.responseText = params['response'] || '';
      console.log('Response text set:', this.responseText);

      if (this.responseText.trim() !== '') {
        console.log('Processing response text...');
        this.calculateScore(this.responseText);
        this.formattedResponse = this.formatResponse(this.responseText);
        console.log('Score after calculation:', this.score);
        console.log('Formatted response:', this.formattedResponse);
      } else {
        console.warn('Empty response text received');
      }
    });
  }

  calculateScore(response: string): void {
    console.log('--- calculateScore() called ---');
    console.log('Original response:', response);
    this.score = 0;

    // Loop through the grading criteria and check for matches using improved patterns
    this.gradingCriteria.forEach(criteria => {
      const testResult = criteria.pattern.test(response);
      console.log(`Testing criteria ${criteria.name}:`);
      console.log(`Pattern: ${criteria.pattern}`);
      console.log(`Test result: ${testResult}`);
      
      criteria.matched = testResult;
      if (criteria.matched) {
        this.score += criteria.weight;
        console.log(`✅ Matched! Adding ${criteria.weight}% (New score: ${this.score}%)`);
      } else {
        console.log(`❌ No match for ${criteria.name}`);
      }
    });

    // Dynamic color based on score
    this.scoreColor = this.score >= 80 ? '#4CAF50' : this.score >= 50 ? '#FFC107' : '#F44336';
    console.log('Final score:', this.score);
    console.log('Score color:', this.scoreColor);
    console.log('--- calculateScore() complete ---');
  }

  formatResponse(response: string): SafeHtml {
    console.log('formatResponse() called');
    let formatted = response;

    // Highlight matched criteria in the response text
    this.gradingCriteria.forEach(criteria => {
      if (criteria.matched) {
        console.log(`Highlighting matched criteria: ${criteria.name}`);
        formatted = formatted.replace(criteria.pattern, match => {
          console.log(`Replacing match: ${match}`);
          return `<span class="criteria-match">${match}</span>`;
        });
      }
    });

    // Basic formatting (optional): Convert line breaks to <br/>
    formatted = formatted.replace(/\n/g, '<br/>');

    // Additional formatting for robustness
    formatted = formatted.replace(/(?:\s*\n\s*)+/g, ' ').trim(); // Remove excess whitespace and newlines
    console.log('Formatted response before sanitizing:', formatted);

    const sanitized = this.sanitizer.bypassSecurityTrustHtml(formatted);
    console.log('Sanitized response:', sanitized);
    return sanitized;
  }
}