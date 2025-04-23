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
      name: 'S1: Start-End Node Check', 
      pattern: /(start.*node|end.*node|Start Terminator|End Terminator)/i, 
      weight: 20,
      matched: false
    },
    { 
      name: 'S2: Unique Sequential Node IDs Check', 
      pattern: /(unique.*id|sequential.*id|node.*identifier)/i, 
      weight: 15,
      matched: false
    },
    { 
      name: 'S3: Valid Node Types Check', 
      pattern: /(valid.*node.*type|start|end|process|decision)/i, 
      weight: 15,
      matched: false
    },
    { 
      name: 'S4: Connected Nodes Check', 
      pattern: /(connected.*nodes|no.*isolated.*node)/i, 
      weight: 15,
      matched: false
    },
    { 
      name: 'S5: Decision Node Outgoing Edges Check', 
      pattern: /(decision.*node.*two.*outgoing|yes.*no)/i, 
      weight: 10,
      matched: false
    },
    { 
      name: 'S6: Clear Labels Check', 
      pattern: /(clear.*label|meaningful.*label)/i, 
      weight: 10,
      matched: false
    },
    { 
      name: 'S7: Complete Path from Start to End Check', 
      pattern: /(complete.*path.*start.*end|reachable.*end)/i, 
      weight: 15,
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
          this.formattedResponse = this.formatResponse(this.responseText);
          this.calculateScore(this.responseText);
        }
      });
    });
  }

  calculateScore(response: string) {
    this.score = 0;
    
    this.gradingCriteria.forEach(criteria => {
      criteria.matched = criteria.pattern.test(response);
      if (criteria.matched) {
        this.score += criteria.weight;
      }
    });

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

    formattedText = formattedText.replace(/\*\s*(.*?)\n/g, '<li>$1</li>');
    formattedText = `<ul>${formattedText}</ul>`;

    const highlightPhrases = ['Read:', 'If', 'Result =', 'Beg =', 'End =', 'Mid ='];
    highlightPhrases.forEach(phrase => {
      formattedText = formattedText.replace(new RegExp(phrase, 'g'), `<strong>${phrase}</strong>`);
    });

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
