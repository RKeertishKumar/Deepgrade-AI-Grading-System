import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';


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
  detailedFeedback: string[] = [];
  showDetails: boolean = false;

  gradingCriteria: any[] = [
    {
      name: 'S1: Start-End Node Check',
      patterns: [
        /start|end/i,
        /begin|finish/i,
        /first.*last/i
      ],
      weight: 20,
      matched: false,
      feedback: {
        positive: 'Start and end nodes mentioned',
        negative: 'Start or end nodes not clearly mentioned'
      }
    },
    {
      name: 'S2: Node IDs Check',
      patterns: [
        /id/i,
        /number/i,
        /identif/i
      ],
      weight: 15,
      matched: false,
      feedback: {
        positive: 'Node identification mentioned',
        negative: 'Node identification not discussed'
      }
    },
    {
      name: 'S3: Node Types Check',
      patterns: [
        /node/i,
        /type/i,
        /start|end|process|decision/i
      ],
      weight: 15,
      matched: false,
      feedback: {
        positive: 'Node types referenced',
        negative: 'Node types not specified'
      }
    },
    {
      name: 'S4: Node Connections',
      patterns: [
        /connect/i,
        /arrow/i,
        /flow/i
      ],
      weight: 15,
      matched: false,
      feedback: {
        positive: 'Node connections mentioned',
        negative: 'Node connections not addressed'
      }
    },
    {
      name: 'S5: Decision Branches',
      patterns: [
        /decision/i,
        /branch/i,
        /yes|no/i
      ],
      weight: 10,
      matched: false,
      feedback: {
        positive: 'Decision branches referenced',
        negative: 'Decision branching not mentioned'
      }
    },
    {
      name: 'S6: Node Labels',
      patterns: [
        /label/i,
        /name/i,
        /description/i
      ],
      weight: 10,
      matched: false,
      feedback: {
        positive: 'Labels discussed',
        negative: 'Labels not addressed'
      }
    },
    {
      name: 'S7: Flow Completion',
      patterns: [
        /path/i,
        /start.*end/i,
        /flow/i
      ],
      weight: 15,
      matched: false,
      feedback: {
        positive: 'Flow completion mentioned',
        negative: 'Flow completion not discussed'
      }
    }
  ];

  constructor(
    private route: ActivatedRoute,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.responseText = params['response'] || '';
      this.detailedFeedback = [];

      if (this.responseText.trim() !== '') {
        const processedText = this.preprocessResponse(this.responseText);
        this.calculateScore(processedText);
        this.generateDetailedFeedback();
        this.formattedResponse = this.formatResponse(processedText);
      }
    });
  }

  private preprocessResponse(response: string): string {
    return response
      .toLowerCase()
      .replace(/\s{2,}/g, ' ')
      .replace(/\n/g, ' ')
      .trim();
  }

  calculateScore(processedResponse: string): void {
    // Base score to make 50% easier to achieve
    const baseScore = 30;
    let keywordMatches = 0;
    const totalKeywords = this.gradingCriteria.reduce((sum, criteria) => sum + criteria.patterns.length, 0);

    // Count all keyword matches
    this.gradingCriteria.forEach(criteria => {
      criteria.patterns.forEach((pattern: RegExp) => {
        if (pattern.test(processedResponse)) {
          keywordMatches++;
        }
      });
    });

    // More generous keyword percentage
    const keywordPercentage = (keywordMatches / totalKeywords) * 50;

    // Criteria matching with lower threshold
    let criteriaMatches = 0;
    this.gradingCriteria.forEach(criteria => {
      criteria.matched = criteria.patterns.some((pattern: RegExp) => pattern.test(processedResponse));
      if (criteria.matched) criteriaMatches++;
    });

    // More generous criteria weighting
    const criteriaPercentage = (criteriaMatches / this.gradingCriteria.length) * 20;

    // Combined score calculation
    this.score = Math.floor(Math.min(baseScore + keywordPercentage + criteriaPercentage, this.maxScore));
    this.setScoreColor();
  }

  private setScoreColor(): void {
    // Adjusted thresholds for colors
    if (this.score >= 50) {
      this.scoreColor = '#4CAF50'; // Green for 50+
    } else if (this.score >= 30) {
      this.scoreColor = '#FFC107'; // Yellow for 30-49
    } else {
      this.scoreColor = '#F44336'; // Red below 30
    }
  }

  private generateDetailedFeedback(): void {
    this.gradingCriteria.forEach(criteria => {
      const feedback = criteria.matched ? criteria.feedback.positive : criteria.feedback.negative;
      this.detailedFeedback.push(`${criteria.name}: ${feedback}`);
    });

    // More generous feedback messages
    if (this.score >= 50) {
      this.detailedFeedback.push('Overall: Good response that covers basic requirements');
    } else if (this.score >= 30) {
      this.detailedFeedback.push('Overall: Acceptable response with some relevant points');
    } else {
      this.detailedFeedback.push('Overall: Response needs more detail about the flowchart');
    }
  }

  formatResponse(response: string): SafeHtml {
    let formatted = response;

    this.gradingCriteria.forEach(criteria => {
      criteria.patterns.forEach((pattern: RegExp) => {
        formatted = formatted.replace(new RegExp(pattern.source, 'gi'), match => {
          return `<span class="keyword-match" title="Relevant term">${match}</span>`;
        });
      });
    });

    formatted = formatted
      .replace(/\n/g, '<br/>')
      .replace(/\b(start|end|node|edge|decision|process|label)\b/gi, '<strong>$1</strong>');

    return this.sanitizer.bypassSecurityTrustHtml(formatted);
  }

  toggleDetails(): void {
    this.showDetails = !this.showDetails;
  }
}