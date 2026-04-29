#!/usr/bin/env python3
"""
Email Classifier for AI Job Foundry
Automatically classifies incoming emails into categories and routes to appropriate processor

Categories:
1. JOB_BULLETIN - Multi-job emails (Glassdoor, LinkedIn, Indeed)
2. INDIVIDUAL_JOB - Single job from recruiter
3. MANUAL_SUBMISSION - Self-forwarded URLs
4. INTERVIEW_NOTIFICATION - Interview scheduling/confirmation
5. REJECTION - Rejection notices
6. SPAM_IRRELEVANT - Spam or non-job emails

Author: Claude + Marcos
Version: 1.0
Date: 2025-11-30
"""

import re
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

class EmailType(Enum):
    """Email classification types"""
    JOB_BULLETIN = "bulletin"
    INDIVIDUAL_JOB = "individual"
    MANUAL_SUBMISSION = "manual"
    INTERVIEW_NOTIFICATION = "interview"
    REJECTION = "rejection"
    SPAM_IRRELEVANT = "spam"

@dataclass
class EmailClassification:
    """Result of email classification"""
    type: EmailType
    confidence: float  # 0.0 to 1.0
    reason: str
    processor: str  # Which script should handle it
    
class EmailClassifier:
    """Classifies job-related emails"""
    
    def __init__(self):
        # Bulletin senders
        self.bulletin_senders = [
            "noreply@glassdoor.com",
            "jobalerts-noreply@linkedin.com",
            "noreply@indeed.com"
        ]
        
        # Interview keywords (Spanish + English)
        self.interview_keywords = [
            # Spanish
            "entrevista", "interview", "técnica", "technical",
            "programada", "scheduled", "confirmación", "confirmation",
            "reunión", "meeting", "videollamada", "video call",
            "zoom", "teams", "google meet", "webex",
            
            # English
            "phone screen", "screening", "assessment", "coding challenge",
            "take-home", "onsite", "on-site", "panel interview"
        ]
        
        # Rejection keywords (Spanish + English)
        self.rejection_keywords = [
            # Spanish
            "no longer accepting", "position filled", "otro candidato",
            "other candidate", "not moving forward", "no seguiremos",
            "lamentamos informar", "regret to inform",
            
            # English
            "unfortunately", "not selected", "pursuing other",
            "decided to move forward with", "at this time"
        ]
        
        # Bulletin subject patterns
        self.bulletin_patterns = [
            r"están contratando",  # Glassdoor Spanish
            r"is hiring",          # LinkedIn English
            r"new jobs? (match|for)",  # Indeed/LinkedIn
            r"\d+ (empleos?|jobs?) (nuevos?|for)",  # Multiple jobs
        ]
        
    def classify(self, 
                 subject: str, 
                 sender: str, 
                 body: str, 
                 to_address: Optional[str] = None) -> EmailClassification:
        """
        Classify an email based on subject, sender, body
        
        Args:
            subject: Email subject line
            sender: From address
            body: Email body (text or HTML)
            to_address: To address (optional, for detecting self-forwards)
            
        Returns:
            EmailClassification with type, confidence, reason, processor
        """
        subject_lower = subject.lower()
        body_lower = body.lower()
        
        # 1. Check for MANUAL_SUBMISSION (self-forwarded URLs)
        if self._is_manual_submission(sender, body, to_address):
            return EmailClassification(
                type=EmailType.MANUAL_SUBMISSION,
                confidence=0.95,
                reason="Self-forwarded LinkedIn URL",
                processor="manual_submission_handler.py"
            )
        
        # 2. Check for JOB_BULLETIN (multi-job emails)
        if self._is_bulletin(sender, subject, body):
            return EmailClassification(
                type=EmailType.JOB_BULLETIN,
                confidence=0.9,
                reason=f"Bulletin from {sender}",
                processor="job_bulletin_processor.py"
            )
        
        # 3. Check for INTERVIEW_NOTIFICATION
        if self._is_interview(subject, body):
            return EmailClassification(
                type=EmailType.INTERVIEW_NOTIFICATION,
                confidence=0.85,
                reason="Contains interview keywords",
                processor="update_status_from_emails.py"
            )
        
        # 4. Check for REJECTION
        if self._is_rejection(subject, body):
            return EmailClassification(
                type=EmailType.REJECTION,
                confidence=0.8,
                reason="Contains rejection keywords",
                processor="mark_all_negatives.py"
            )
        
        # 5. Check for SPAM/IRRELEVANT
        if self._is_spam(subject, body):
            return EmailClassification(
                type=EmailType.SPAM_IRRELEVANT,
                confidence=0.7,
                reason="Appears to be spam or irrelevant",
                processor="ignore"
            )
        
        # 6. Default: INDIVIDUAL_JOB
        return EmailClassification(
            type=EmailType.INDIVIDUAL_JOB,
            confidence=0.6,
            reason="Default classification",
            processor="ingest_email_to_sheet_v2.py"
        )
    
    def _is_manual_submission(self, sender: str, body: str, to_address: Optional[str]) -> bool:
        """Check if email is self-forwarded URL"""
        # Check if sender is user themselves
        is_self_sent = "markalvati@gmail.com" in sender.lower()
        
        # Check if body is just a LinkedIn URL
        body_clean = body.strip()
        is_linkedin_url = bool(re.match(r'^https://www\.linkedin\.com/jobs/view/\d+/?$', body_clean))
        
        return is_self_sent and is_linkedin_url
    
    def _is_bulletin(self, sender: str, subject: str, body: str) -> bool:
        """Check if email is a job bulletin (multiple jobs)"""
        # Check sender
        if any(bulletin_sender in sender.lower() for bulletin_sender in self.bulletin_senders):
            return True
        
        # Check subject patterns
        for pattern in self.bulletin_patterns:
            if re.search(pattern, subject, re.IGNORECASE):
                return True
        
        # Check if body contains multiple job URLs (3+)
        linkedin_urls = re.findall(r'https://www\.linkedin\.com/jobs/view/\d+', body)
        if len(linkedin_urls) >= 3:
            return True
        
        return False
    
    def _is_interview(self, subject: str, body: str) -> bool:
        """Check if email is interview notification"""
        text = (subject + " " + body).lower()
        
        # Count interview keyword matches
        matches = sum(1 for kw in self.interview_keywords if kw in text)
        
        # High confidence if 2+ keywords
        return matches >= 2
    
    def _is_rejection(self, subject: str, body: str) -> bool:
        """Check if email is rejection notice"""
        text = (subject + " " + body).lower()
        
        # Count rejection keyword matches
        matches = sum(1 for kw in self.rejection_keywords if kw in text)
        
        # High confidence if 1+ keywords
        return matches >= 1
    
    def _is_spam(self, subject: str, body: str) -> bool:
        """Check if email is spam or irrelevant"""
        spam_indicators = [
            # Marketing spam
            "unsubscribe", "opt out", "remove from list",
            "click here", "limited time offer",
            
            # Promotional
            "special offer", "discount", "sale ending",
            "free trial", "download now",
            
            # Too generic
            len(subject) < 10,  # Very short subject
            len(body) < 50,     # Very short body
        ]
        
        text = (subject + " " + body).lower()
        
        # Check indicators
        matches = sum(1 for indicator in spam_indicators[:10] if indicator in text)
        
        # Add short length penalties
        if len(subject) < 10:
            matches += 1
        if len(body) < 50:
            matches += 1
        
        return matches >= 2


# CLI for testing
if __name__ == "__main__":
    import sys
    
    classifier = EmailClassifier()
    
    # Test cases
    test_cases = [
        {
            "name": "Glassdoor Bulletin",
            "subject": "Tech Holding y otros están contratando en Guadalajara",
            "sender": "noreply@glassdoor.com",
            "body": "Oracle está contratando\nIT Project Manager\nTech Holding\nSenior PM..."
        },
        {
            "name": "Self-forwarded URL",
            "subject": "https://www.linkedin.com/jobs/view/4339365751/",
            "sender": "markalvati@gmail.com",
            "body": "https://www.linkedin.com/jobs/view/4339365751/"
        },
        {
            "name": "Interview Notification",
            "subject": "Technical Interview - Friday Nov 28",
            "sender": "recruiter@epam.com",
            "body": "We would like to schedule a technical interview with you on Friday..."
        },
        {
            "name": "Rejection",
            "subject": "Application Update",
            "sender": "noreply@company.com",
            "body": "Thank you for your interest. Unfortunately, we decided to move forward with other candidates..."
        },
        {
            "name": "Individual Job",
            "subject": "Senior PM Role at Google",
            "sender": "recruiter@google.com",
            "body": "Hi Marcos, I came across your profile and think you'd be great for our Senior PM role..."
        }
    ]
    
    print("=" * 80)
    print("EMAIL CLASSIFIER - TEST RESULTS")
    print("=" * 80)
    
    for test in test_cases:
        print(f"\n📧 Test: {test['name']}")
        print(f"   Subject: {test['subject'][:50]}...")
        print(f"   Sender: {test['sender']}")
        
        result = classifier.classify(
            subject=test['subject'],
            sender=test['sender'],
            body=test['body']
        )
        
        print(f"   ➜ Type: {result.type.value}")
        print(f"   ➜ Confidence: {result.confidence*100:.0f}%")
        print(f"   ➜ Reason: {result.reason}")
        print(f"   ➜ Processor: {result.processor}")
    
    print("\n" + "=" * 80)
    print("✅ Tests completed!")
