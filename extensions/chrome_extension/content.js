// Content script to extract job posting text from web pages
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractJobText') {
        const jobText = extractJobPostingText();
        sendResponse({ jobText: jobText });
    }
});

function extractJobPostingText() {
    // Fast check: Is this likely a job posting page?
    if (!isJobPostingPage()) {
        return "Not a job posting page";
    }

    // Priority selectors - most specific first
    const prioritySelectors = [
        '[data-test-id="job-description"]',
        '.jobs-description__content',
        '#jobDescriptionText',
        '.jobDescriptionContent',
        '.job-description',
        '.job-detail',
        '.vacancy-description'
    ];

    // Try priority selectors first (fast path)
    for (const selector of prioritySelectors) {
        const element = document.querySelector(selector);
        if (element) {
            const text = element.textContent.trim();
            if (text.length > 100) {
                return cleanText(text);
            }
        }
    }

    // Fast fallback: Look for content containers
    const contentSelectors = [
        'article',
        '.content',
        '.main-content',
        '[class*="description"]',
        '[id*="description"]'
    ];

    for (const selector of contentSelectors) {
        const element = document.querySelector(selector);
        if (element) {
            const text = element.textContent.trim();
            if (text.length > 200) {
                return cleanText(text);
            }
        }
    }

    // Ultra-fast final fallback: Get largest text block (limit to first 50 elements)
    const textElements = Array.from(document.querySelectorAll('p, div:not(nav, header, footer, aside, .sidebar)'))
        .slice(0, 50) // Limit to prevent slow processing
        .filter(el => {
            const text = el.textContent.trim();
            return text.length > 150 &&
                   !el.querySelector('button, input, select, nav, header, footer') &&
                   !el.closest('nav, header, footer, aside, .sidebar');
        })
        .map(el => ({
            text: el.textContent.trim(),
            length: el.textContent.trim().length
        }))
        .sort((a, b) => b.length - a.length);

    if (textElements.length > 0) {
        return cleanText(textElements[0].text);
    }

    // Emergency fallback
    return cleanText(document.body.innerText || document.body.textContent || "");
}

function cleanText(text) {
    if (!text) return "";
    // Fast cleanup: single pass regex
    return text
        .replace(/\s+/g, ' ') // Multiple whitespace to single space
        .replace(/\n\s*\n/g, '\n') // Multiple newlines to single
        .trim()
        .substring(0, 8000); // Reasonable limit for API
}

function isJobPostingPage() {
    const url = window.location.href.toLowerCase();
    const title = document.title.toLowerCase();

    // Fast keyword checks
    const jobKeywords = ['job', 'career', 'vacancy', 'position', 'hiring', 'employment', 'opening'];
    const urlIndicators = ['job', 'vacancy', 'career', 'hiring', 'indeed', 'linkedin', 'glassdoor', 'monster', 'dice'];

    return jobKeywords.some(keyword => title.includes(keyword)) ||
           urlIndicators.some(indicator => url.includes(indicator)) ||
           document.querySelector('[data-test-id="job-description"], #jobDescriptionText, .jobDescriptionContent');
}