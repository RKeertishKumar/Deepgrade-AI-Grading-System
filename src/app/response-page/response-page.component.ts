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
  gradingCriteria: any[] = [
    { 
      name: 'Correct Algorithm', 
      pattern: /(correct algorithm|proper steps|accurate logic)/i, 
      weight: 30,
      matched: false
    },
    { 
      name: 'Flowchart Structure', 
      pattern: /(begin|start|end|terminator|decision|process)/i, 
      weight: 25,
      matched: false
    },
    { 
      name: 'Variable Usage', 
      pattern: /(variable|declare|initialize|assign)/i, 
      weight: 20,
      matched: false
    },
    { 
      name: 'Loop Logic', 
      pattern: /(while|for|loop|repeat|until)/i, 
      weight: 15,
      matched: false
    },
    { 
      name: 'Output Mention', 
      pattern: /(output|print|display|result)/i, 
      weight: 10,
      matched: false
    }
  ];

  constructor(
    private route: ActivatedRoute,
    private sanitizer: DomSanitizer,
    private gradingService: GradingService
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.responseText = params['response'];
      this.gradingService.gradeResponse(this.responseText).subscribe({
        next: (result) => {
          this.score = result.score;
          this.maxScore = result.max_score;
          this.scoreColor = result.score_color;
          this.formattedResponse = this.sanitizer.bypassSecurityTrustHtml(result.formatted_response);
          
          // Update criteria matches
          this.gradingCriteria.forEach(criteria => {
            criteria.matched = result.matched_criteria.includes(criteria.name);
          });
        },
        error: (err) => {
          console.error('Error grading response:', err);
          // Fallback to client-side grading
          this.formattedResponse = this.formatResponse(this.responseText);
          this.calculateScore(this.responseText);
        }
      });
    });
  }

  calculateScore(response: string) {
    this.score = 0;
    
    // Check each grading criteria
    this.gradingCriteria.forEach(criteria => {
      criteria.matched = criteria.pattern.test(response);
      if (criteria.matched) {
        this.score += criteria.weight;
      }
    });

    // Set score color based on performance
    if (this.score >= 80) {
      this.scoreColor = '#4CAF50'; // Green
    } else if (this.score >= 50) {
      this.scoreColor = '#FFC107'; // Yellow
    } else {
      this.scoreColor = '#F44336'; // Red
    }
  }

  formatResponse(response: string): SafeHtml {
    let formattedText = response;

    // Replace * with <li> for bullet points
    formattedText = formattedText.replace(/\*\s*(.*?)\n/g, '<li>$1</li>');

    // Wrap the entire content in a <ul> tag
    formattedText = `<ul>${formattedText}</ul>`;

    // Highlight key phrases
    const highlightPhrases = ['Read:', 'If', 'Result =', 'Beg =', 'End =', 'Mid ='];
    highlightPhrases.forEach(phrase => {
      formattedText = formattedText.replace(new RegExp(phrase, 'g'), `<strong>${phrase}</strong>`);
    });

    // Highlight grading criteria matches
    this.gradingCriteria.forEach(criteria => {
      if (criteria.matched) {
        formattedText = formattedText.replace(criteria.pattern, match => 
          `<span class="criteria-match">${match}</span>`
        );
      }
    });

    return this.sanitizer.bypassSecurityTrustHtml(formattedText);
  }
}