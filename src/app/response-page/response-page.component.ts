import { Component, OnInit } from '@angular/core';
import { ResponseService } from '../../services/reposneshare.service';
import { ActivatedRoute } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  selector: 'app-response-page',
  templateUrl: './response-page.component.html',
  styleUrl: './response-page.component.scss'
})
export class ResponsePageComponent implements OnInit {
  responseText: string = '';
  formattedResponse: SafeHtml = '';

  constructor(private route: ActivatedRoute, private sanitizer: DomSanitizer) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.responseText = params['response']; // Retrieve the response from query params
      this.formattedResponse = this.formatResponse(this.responseText); // Format the response
    });
  }

  // Function to format the response text
  formatResponse(response: string): SafeHtml {
    let formattedText = response;

    // Replace * with <li> for bullet points
    formattedText = formattedText.replace(/\*\s*(.*?)\n/g, '<li>$1</li>');

    // Wrap the entire content in a <ul> tag
    formattedText = `<ul>${formattedText}</ul>`;

    // Highlight key phrases (e.g., "Read:", "If", "Result =")
    const highlightPhrases = ['Read:', 'If', 'Result =', 'Beg =', 'End =', 'Mid ='];
    highlightPhrases.forEach(phrase => {
      formattedText = formattedText.replace(new RegExp(phrase, 'g'), `<strong>${phrase}</strong>`);
    });

    // Sanitize the HTML to prevent XSS attacks
    return this.sanitizer.bypassSecurityTrustHtml(formattedText);
  }
}
