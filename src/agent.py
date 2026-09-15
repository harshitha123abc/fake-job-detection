# src/agent.py
import os
import re
import json
import requests
import openai
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()
openai_client = None
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

class JobExtractorAgent:
    """Agent 1: Extracts key information from job postings"""

    def extract(self, text: str) -> Dict:
        """Extract company name, role, salary, location from job text using AI"""
        
        # Detect if this is an email or job posting
        is_email = self._is_email_format(text)
        
        # Clean email headers if needed
        if is_email:
            text = self._clean_email_text(text)
        
        # Try AI extraction first
        ai_result = self._extract_with_ai(text)
        if ai_result:
            ai_result["is_email"] = is_email
            return ai_result
        
        # Fallback to rule-based extraction
        company = self._extract_company(text)
        role = self._extract_role(text)
        salary = self._extract_salary(text)
        location = self._extract_location(text)

        return {
            "company": company,
            "role": role,
            "salary": salary,
            "location": location,
            "extraction_confidence": self._calculate_confidence(company, role, salary, location),
            "is_email": is_email
        }

    def _extract_with_ai(self, text: str) -> Optional[Dict]:
        """Use OpenAI to extract job information for better accuracy"""
        return None

    def _is_email_format(self, text: str) -> bool:
        """Detect if text is email format (vs job posting)"""
        email_indicators = [
            r'(?:Dear|Hi|Hello)\s+[A-Z]',  # Email greeting
            r'(?:Subject|Re:|Fwd:)',        # Email subject
            r'(?:Regards|Yours|Thank you)',  # Email closing
            r'(?:regards|best|sincerely)',
            r'email|@.*\.(?:com|org|in|co)',  # Email addresses
            r'(?:Application Status|Application Update)',
            r'^[A-Z][A-Za-z\s]+(?:Status|Update|Notification)$',  # Subject-like line
        ]
        
        indicators_found = sum(1 for pattern in email_indicators if re.search(pattern, text, re.MULTILINE | re.IGNORECASE))
        return indicators_found >= 2

    def _clean_email_text(self, text: str) -> str:
        """Remove email headers and subject lines"""
        lines = text.split('\n')
        
        # Skip subject and header lines
        skip_patterns = [
            r'^[A-Z][A-Za-z\s]+?\s+(?:Status|Update|Logo|Notification)',
            r'^(?:Dear|Hello|Hi|Subject|From|To|CC|Date)',
            r'^(?:[A-Z][A-Za-z\s]+?\s+(?:Logo|Image))',
        ]
        
        cleaned_lines = []
        for line in lines:
            skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    skip = True
                    break
            if not skip and line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def _extract_company(self, text: str) -> str:
        """
        Extract company name using intelligent heuristics.
        Works across different job posting formats.
        """
        
        # Comprehensive list of section headers and keywords to exclude
        section_keywords = {
            # Common headers
            'job', 'role', 'position', 'title', 'hiring', 'opportunity', 'opening',
            'eligibility', 'requirement', 'requirements', 'ctc', 'salary', 'pay',
            'compensation', 'location', 'locations', 'based', 'work', 'remote',
            'skills', 'process', 'selection', 'assessment', 'interview',
            'registration', 'deadline', 'batch', 'campus', 'drive', 'campus',
            'virtual', 'physical', 'application', 'apply', 'company',
            'about', 'description', 'objective', 'summary', 'overview',
            'experience', 'education', 'contact', 'info', 'information',
            'hosted', 'on', 'strong', 'understanding', 'knowledge', 'familiarity',
            'excellent', 'ability', 'abilities', 'skill', 'team', 'teamwork',
            'problem', 'solving', 'critical', 'thinking', 'communication',
            'date', 'created', 'posted', 'updated', 'time', 'from', 'to',
            'degree', 'bachelor', 'master', 'diploma', 'btech', 'btech',
            'secondary', 'primary', 'preliminary', 'technical', 'hr',
            'action', 'preferred', 'details', 'below', 'following', 'next',
            'learn', 'love', 'build', 'join', 'work', 'help', 'create'
        }

        # Step 1: Check for explicit "Company:" labels
        explicit_match = re.search(
            r"(?:Company|Hiring by|Employer|Hired by|Organization|Client):\s*\*?([^\n,*]+?)(?:\n|$)",
            text, re.IGNORECASE
        )
        if explicit_match:
            company = explicit_match.group(1).strip()
            company = re.sub(r'[\*\-_]', '', company).strip()
            if len(company) > 2 and company.lower() not in section_keywords:
                return company

        # Step 2: Extract from first line (most likely to contain company name)
        lines = text.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            
            # Remove markdown formatting
            first_line_clean = re.sub(r'[\*_]+', '', first_line)
            
            # Extract company from first line
            company_from_first = self._extract_from_line(first_line_clean, section_keywords)
            if company_from_first and company_from_first.lower() not in section_keywords:
                return company_from_first

        # Step 3: Look through first 15 lines for company mentions
        for line in lines[:15]:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip obvious section headers (lines with colons followed by specific keywords)
            if ':' in line:
                header_match = re.match(r'^([^:]+):', line)
                if header_match:
                    header_text = header_match.group(1).lower().strip()
                    # If header is a known section keyword, skip this line
                    if any(kw in header_text for kw in ['job', 'role', 'position', 'eligibility', 
                                                          'requirement', 'skill', 'process', 'selection']):
                        continue
            
            # Try to extract company candidate
            company_candidate = self._extract_from_line(line, section_keywords)
            if company_candidate and company_candidate.lower() not in section_keywords:
                return company_candidate

        # Step 4: If nothing found, look for company suffix patterns
        company_patterns = re.findall(
            r'\b([A-Z][A-Za-z0-9&\.\s]*?)\s+(?:Inc|Ltd|LLC|Corp|Corporation|Co\.|Limited|Pvt|Private|Technologies|Solutions|Systems|Software|Services)\b',
            text
        )
        if company_patterns:
            # Return the first (most likely) match
            return company_patterns[0].strip()

        return "Unknown"

    def _extract_from_line(self, line: str, section_keywords: set) -> Optional[str]:
        """
        Extract a potential company name from a single line.
        Returns None if no valid candidate found.
        """
        # Remove markdown and special characters
        line_clean = re.sub(r'[\*_`~\-]+', '', line).strip()
        
        if not line_clean:
            return None
        
        # Get first 1-2 capitalized words/phrase
        words = line_clean.split()
        
        if not words:
            return None
        
        capitalized_words = []
        for word in words:
            # Skip pure numbers or year-like patterns (e.g., "2027")
            if word.isdigit() and len(word) == 4:
                break
            
            # Stop if we hit a lowercase word (likely not part of company name)
            if word and word[0].islower() and not word.lower() in ['&', 'and', 'or']:
                # Exception: if very first word is lowercase (bad formatting), still try it
                if len(capitalized_words) > 0:
                    break
            
            # Stop if we hit certain keywords (like "Virtual", "On", "Campus")
            if word.lower() in ['virtual', 'on', 'drive', 'batch', 'campus', 'opportunity',
                               'physical', 'online', 'hybrid', 'inaugural',
                               'job', 'role', 'position', 'for', 'the', 'a', 'an', 'is',
                               'are', 'recruitment', 'hiring', 'we', 'looking']:
                break
            
            # Add valid capitalized or special word (&,-)
            if word.lower() in ['&', 'and', 'or']:
                capitalized_words.append(word)
            elif word and (word[0].isupper() or (len(capitalized_words) == 0 and word[0].islower())):
                capitalized_words.append(word)
                # Usually company names are 1-3 words max
                if len(capitalized_words) >= 3:
                    break
        
        if capitalized_words:
            candidate = ' '.join(capitalized_words).strip()
            
            # Validation checks
            if (len(candidate) > 2 and len(candidate) < 100 and
                candidate.lower() not in section_keywords and
                not any(kw in candidate.lower() for kw in ['batch', 'virtual', 'on campus'])):
                return candidate
        
        return None

    def _extract_role(self, text: str) -> str:
        """Extract job role/title - improved for emails and postings"""
        patterns = [
            # Email pattern: "for the [ROLE] position"
            r"for\s+(?:a|the)?\s+([A-Z][A-Za-z\s&()]{2,60})(?:\s+(?:position|role|opening))",
            # Email pattern: "position at [COMPANY]" - extract before "position"
            r"(?:the\s+)?([A-Za-z\s&()]+?)\s+position\s+at",
            # Direct label
            r"(?:Position|Title|Role|Job|Job Roles?|Job profile):\s*\*?\s*([A-Z][A-Za-z\s&()]{2,50}?)(?:\s*[.,]|$|\n)",
            # Standard hiring pattern
            r"(?:Hiring|Looking for|Seeking)\s+([A-Z][A-Za-z\s&]{2,50})",
            # Numbered list
            r"^\d+\.\s*\*?\s*([A-Z][A-Za-z\s&/.()]{2,40})(?:\s*[.,]|$)",
            # Well-known roles
            r"((?:Software Engineer|Full Stack Developer|Frontend Developer|Backend Developer|Data Scientist|Machine Learning Engineer|AI Engineer|DevOps Engineer|SDE|Java Developer|Python Developer|Senior Developer|Intern)(?:\s+[A-Za-z\s&()]{0,30})?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                role = match.group(1).strip()
                # Remove markdown and clean up
                role = re.sub(r'[\*\-_]', '', role)
                role = re.sub(r'\s+', ' ', role)
                # Remove common prefixes/suffixes
                role = re.sub(r'^(Position|Title|Role|Job|Profile|The|A|An)[:\-]?\s*', '', role, flags=re.IGNORECASE)
                # Remove unwanted continuations
                if any(word in role.lower() for word in ['onwards', 'from', 'throughout', 'during', 'till', 'until', 'only', 'and above', 'percentage', 'batch', 'backlogs', 'has', 'progressed', 'completed']):
                    continue
                # Validate: length and no garbage
                if len(role) > 3 and len(role) < 80 and not role.lower().startswith(('the ', 'and ', 'but ', 'or ', 'company')):
                    return role

        return "Not specified"

    def _extract_salary(self, text: str) -> str:
        """Extract salary information"""
        patterns = [
            r"(?:Salary|Pay|Compensation|CTC|Stipend|Salary Package|Package)\s*(?:upto|up to|from|between)?\s*[:\-]?\s*([^\n,*]+)",
            r"(?:₹|\$|Rs\.?)\s*[\d,]+(?:\.\d+)?(?:\s*-\s*[\d,]+(?:\.\d+)?)?(?:\s*(?:LPA|k|lakhs?|lacs?|per\s+(?:month|year|hour|day)))?",
            r"[\d,]+(?:\.\d+)?(?:\s*-\s*[\d,]+(?:\.\d+)?)?\s*(?:₹|\$|Rs\.?|LPA|k)(?:\s*per\s+(?:month|year|hour|day))?",
            r"[\d,]+(?:\.\d+)?(?:\s*-\s*[\d,]+(?:\.\d+)?)?\s*LPA",
            r"[\d,]+(?:\.\d+)?(?:\s*-\s*[\d,]+(?:\.\d+)?)?\s*k",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary = match.group(1).strip() if match.groups() else match.group(0).strip()
                # Clean up markdown and extra spaces
                salary = re.sub(r'[\*\-_]', '', salary)
                salary = re.sub(r'\s+', ' ', salary)
                # Remove common prefixes
                salary = re.sub(r'^(Salary|Pay|Compensation|CTC|Stipend|Package)[:\-]?\s*', '', salary, flags=re.IGNORECASE)
                # Normalize common units
                salary = re.sub(r'\b(lakhs?|lacs?)\b', 'LPA', salary, flags=re.IGNORECASE)
                if len(salary) > 2 and any(char.isdigit() for char in salary):
                    return salary

        return "Not specified"

    def _extract_location(self, text: str) -> str:
        """Extract location information - with validation"""
        invalid_locations = {"venue", "office", "on-site", "remote", "hybrid", "work from home", "wfh"}
        
        patterns = [
            # Direct labels
            r"(?:Location|City|Place|Based in):\s*\*?\s*([^\n,*]{2,50})",
            r"(?:Location|City|Place|Based in):\s*\*?\s*\n+\s*([^\n,*]{2,50})",
            # Geographic pattern
            r"(?:in|at)\s+([A-Z][A-Za-z\s,]{2,40})(?:\s*\(|,|\.|$)",
            # With line break
            r"(?:Location|City|Place|Based in)\s*\*?\s*\n+\s*\*?\s*([A-Z][A-Za-z\s,]{2,40})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                
                # Clean up markdown formatting
                location = re.sub(r'[\*\-_]', '', location)
                location = re.sub(r'\s+', ' ', location)
                
                # Remove common prefixes
                location = re.sub(r'^(Location|City|Place|Based)[:\-]?\s*', '', location, flags=re.IGNORECASE)
                
                # Validate: reasonable length and no email garbage
                invalid_phrases = ['has', 'progressed', 'completed', 'requirements', 'eligibility', 'qualifications', 'application', 'stage']
                if any(phrase in location.lower() for phrase in invalid_phrases):
                    continue
                    
                if len(location) > 2 and len(location) < 50 and not location.lower().startswith(('the ', 'and ', 'but ', 'or ')) and location.lower() not in invalid_locations:
                    return location

        # Check for remote work
        if "remote" in text.lower() or "work from home" in text.lower() or "wfh" in text.lower():
            return "Remote"

        return "Not specified"

    def _calculate_confidence(self, company: str, role: str, salary: str, location: str) -> float:
        """Calculate extraction confidence score"""
        confidence = 0.0

        # Company confidence (30% max)
        if company != "Unknown":
            if len(company) > 5 and any(char.isdigit() for char in company):  # Has numbers, likely real company
                confidence += 0.3
            elif len(company) > 3:
                confidence += 0.25
            else:
                confidence += 0.15

        # Role confidence (30% max)
        if role != "Not specified":
            if len(role) > 10 and any(word in role.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'specialist']):
                confidence += 0.3
            elif len(role) > 5:
                confidence += 0.2
            else:
                confidence += 0.1

        # Salary confidence (20% max)
        if salary != "Not specified":
            if any(unit in salary.upper() for unit in ['LPA', 'K', '₹', 'RS', '$']):
                confidence += 0.2
            elif any(char.isdigit() for char in salary):
                confidence += 0.15
            else:
                confidence += 0.05

        # Location confidence (20% max)
        if location != "Not specified":
            if location == "Remote":
                confidence += 0.2
            elif len(location) > 3 and not any(char.isdigit() for char in location):
                confidence += 0.15
            else:
                confidence += 0.1

        return min(confidence, 1.0)  # Cap at 100%


class CrossPlatformSearchAgent:
    """Agent 2: Searches across platforms to verify job existence"""

    def __init__(self):
        self.google_api_key = GOOGLE_SEARCH_API_KEY
        self.search_engine_id = GOOGLE_SEARCH_ENGINE_ID

    # ── New: detect platform URLs already present in the pasted job text ──────
    def _detect_platforms_in_text(self, raw_text: str) -> List[str]:
        """If the user pasted text from a platform page, extract those platforms directly."""
        text_lower = raw_text.lower()
        mapping = {
            "linkedin.com":     "LinkedIn",
            "indeed.com":       "Indeed",
            "glassdoor.com":    "Glassdoor",
            "naukri.com":       "Naukri",
            "monster.com":      "Monster",
            "dice.com":         "Dice",
            "careerbuilder.com":"CareerBuilder",
            "ziprecruiter.com": "ZipRecruiter",
        }
        return list({name for domain, name in mapping.items() if domain in text_lower})

    def search(self, company: str, role: str, raw_text: str = "") -> Dict:
        """Search for job across platforms using Google Custom Search"""
        # ── 1. Check if the pasted text itself came from a known platform ──────
        platforms_from_text = self._detect_platforms_in_text(raw_text)

        if company == "Unknown":
            if platforms_from_text:
                return {
                    "found_on_platforms": platforms_from_text,
                    "confidence_score": min(len(platforms_from_text) * 0.35, 1.0),
                    "recommendation": "Verified on " + ", ".join(platforms_from_text),
                    "search_results": []
                }
            return {"found_on_platforms": [], "confidence_score": 0.0, "search_results": []}

        # First, search on job platforms
        search_query = f'{company} {role} site:linkedin.com OR site:indeed.com OR site:glassdoor.com OR site:naukri.com OR site:monster.com OR site:dice.com OR site:careerbuilder.com OR site:ziprecruiter.com'

        platforms_found = []
        search_results = []
        company_website_found = False

        try:
            if self.google_api_key and self.search_engine_id:
                results = self._google_search(search_query)
                search_results = results

                # Analyze results for platform presence
                for result in results.get('items', []):
                    url = result.get('link', '').lower()
                    title = result.get('title', '').lower()
                    snippet = result.get('snippet', '').lower()

                    if 'linkedin.com' in url and company.lower() in (title + snippet):
                        platforms_found.append("LinkedIn")
                    elif 'indeed.com' in url and company.lower() in (title + snippet):
                        platforms_found.append("Indeed")
                    elif 'glassdoor.com' in url and company.lower() in (title + snippet):
                        platforms_found.append("Glassdoor")
                    elif 'naukri.com' in url and company.lower() in (title + snippet):
                        platforms_found.append("Naukri")
                    elif 'monster.com' in url and company.lower() in (title + snippet):
                        platforms_found.append("Monster")
                    elif 'dice.com' in url and company.lower() in (title + snippet):
                        platforms_found.append("Dice")
                    elif 'careerbuilder.com' in url and company.lower() in (title + snippet):
                        platforms_found.append("CareerBuilder")
                    elif 'ziprecruiter.com' in url and company.lower() in (title + snippet):
                        platforms_found.append("ZipRecruiter")

                # Remove duplicates
                platforms_found = list(set(platforms_found))

        except Exception as e:
            print(f"Search error: {e}")
            platforms_found = []

        # Merge with platforms detected directly in the pasted text
        for p in platforms_from_text:
            if p not in platforms_found:
                platforms_found.append(p)

        # If not found on job platforms, search company website directly
        # Weight per platform: 0.30 (so 2 platforms = 0.60 = "likely authentic")
        confidence_score = min(len(platforms_found) * 0.30, 1.0)
        
        if confidence_score == 0:
            try:
                # Search for company careers/jobs page
                careers_query = f'"{company}" careers OR jobs OR recruitment site:*.com OR site:*.in OR site:*.co.uk'
                careers_results = self._google_search(careers_query)
                
                if careers_results and careers_results.get('items'):
                    for result in careers_results.get('items', [])[:3]:
                        url = result.get('link', '').lower()
                        # Legitimate recruitment indicators
                        recruitment_keywords = [
                            'career', 'job', 'recruit', 'hiring', 'position', 'apply',
                            'opportunity', 'vacancy', 'opening', 'campus', 'drive'
                        ]
                        
                        title = result.get('title', '').lower()
                        snippet = result.get('snippet', '').lower()
                        content = title + " " + snippet
                        
                        # Check if this looks like a company recruitment page
                        if (any(keyword in content for keyword in recruitment_keywords) and
                            company.lower() in content and
                            '//' not in url.replace('https://', '').replace('http://', '')[:20]):
                            company_website_found = True
                            confidence_score = 0.6  # Company website found with recruitment info
                            platforms_found.append("Company Website")
                            break
                            
            except Exception as e:
                print(f"Company website search error: {e}")

        if confidence_score >= 0.5:
            recommendation = "Likely authentic — found on " + ", ".join(platforms_found)
        elif platforms_found:
            recommendation = "Partially verified on " + ", ".join(platforms_found)
        elif company_website_found:
            recommendation = "Company website found; not listed on major job boards (normal for direct recruitment)"
        else:
            recommendation = "Not found on major platforms — verify through company's official website"

        return {
            "found_on_platforms": platforms_found,
            "confidence_score": confidence_score,
            "search_results": search_results,
            "platforms_checked": ["LinkedIn", "Indeed", "Glassdoor", "Naukri", "Monster", "Dice", "CareerBuilder", "ZipRecruiter", "Company Website"],
            "recommendation": recommendation
        }

    def _google_search(self, query: str) -> Dict:
        """Perform Google Custom Search or fallback to standard Google search."""
        if self.google_api_key and self.search_engine_id:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': 10
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('items'):
                        return result
            except requests.exceptions.RequestException:
                pass

        return self._google_web_search(query)

    def _google_web_search(self, query: str) -> Dict:
        """Fallback search using DuckDuckGo (no API key required)."""
        try:
            from ddgs import DDGS  # type: ignore[import-not-found]
            results = list(DDGS().text(query, max_results=10))
            items = [{'link': r.get('href', ''), 'title': r.get('title', ''), 'snippet': r.get('body', '')}
                     for r in results if r.get('href')]
            return {'items': items}
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return {}


class CompanyVerificationAgent:
    """Agent 3: Verifies company existence and legitimacy"""

    def __init__(self):
        self.google_api_key = GOOGLE_SEARCH_API_KEY
        self.search_engine_id = GOOGLE_SEARCH_ENGINE_ID

    def _google_search(self, query: str) -> Dict:
        """Google Custom Search with DuckDuckGo fallback when quota exceeded."""
        if self.google_api_key and self.search_engine_id:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {'key': self.google_api_key, 'cx': self.search_engine_id, 'q': query, 'num': 5}
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    return response.json()
            except:
                pass
        # DuckDuckGo fallback
        try:
            from ddgs import DDGS  # type: ignore[import-not-found]
            results = list(DDGS().text(query, max_results=5))
            items = [{'link': r.get('href',''), 'title': r.get('title',''), 'snippet': r.get('body','')}
                     for r in results if r.get('href')]
            return {'items': items}
        except:
            return {}

    def _is_campus_drive(self, raw_text: str) -> bool:
        """Detect if posting is a campus drive (inherently legitimate recruitment format)."""
        text_lower = raw_text.lower()
        signals = [
            bool(re.search(r'campus\s+drive', text_lower)),
            bool(re.search(r'\b(2026|2027|2028)\s+batch\b', text_lower)),
            bool(re.search(r'\bblock\s+\d+|floor|auditorium|audi\b', text_lower)),
            bool(re.search(r'\b(btech|b\.tech|be\b|mtech|mca|mba)\b', text_lower)),
            bool(re.search(r'\b(ctc|stipend|lpa)\b', text_lower)),
            bool(re.search(r'selection\s+process', text_lower)),
            bool(re.search(r'pre\s+placement\s+talk|ppt\b', text_lower)),
            bool(re.search(r'no\s+of\s+(?:registered|eligible)\s+students', text_lower)),
            bool(re.search(r'hosted\s+by', text_lower)),
        ]
        return sum(signals) >= 3

    def verify(self, company: str, raw_text: str = "") -> Dict:
        """Verify company website and LinkedIn presence"""
        if company == "Unknown":
            return {
                "website_exists": False,
                "linkedin_exists": False,
                "verification_score": 0.0,
                "flags": ["Company name not extracted"]
            }

        # ── Quick win: detect LinkedIn/company URLs in the pasted text itself ──
        text_lower = raw_text.lower()
        text_li_verified = bool(re.search(r'linkedin\.com/(company|in|jobs)/', text_lower))
        text_web_verified = bool(re.search(r'https?://(?!linkedin|indeed|glassdoor|naukri|monster|dice|careerbuilder|ziprecruiter)\S+\.(com|in|co\.in|co\.uk|org|net)', text_lower))

        # ── Campus drive bonus: structured college drives are inherently real ──
        is_campus = self._is_campus_drive(raw_text)

        # Run the standard checks, but OR with what we found in the text
        website_exists  = text_web_verified or self._check_website_exists(company)
        linkedin_exists = text_li_verified  or self._check_linkedin_exists(company)

        flags = []
        if not website_exists:
            flags.append("No company website found")
        if not linkedin_exists:
            flags.append("No LinkedIn company page found")
        if text_li_verified:
            flags = [f for f in flags if "LinkedIn" not in f]
        if is_campus:
            flags.append("✅ Structured campus drive format detected")

        # Calculate verification score
        score = 0.0
        if website_exists:  score += 0.6
        if linkedin_exists: score += 0.4
        if is_campus:       score = max(score, 0.55)  # campus drives get minimum passing score

        return {
            "website_exists": website_exists,
            "linkedin_exists": linkedin_exists,
            "verification_score": min(score, 1.0),
            "flags": flags,
            "is_campus_drive": is_campus,
            "recommendation": "Company verified" if score >= 0.6 else (
                "Campus drive — verify via college placement cell" if is_campus
                else "Suspicious - limited online presence"
            )
        }

    def _check_website_exists(self, company: str) -> bool:
        """Check if company website exists using multiple methods"""
        try:
            company_normalized = company.lower().strip()
            company_normalized = re.sub(r'\b(pvt\.? ltd\.?|pvt\.?|ltd\.?|limited|inc\.?|corp\.?|corporation|co\.?|llc\.?|l\.l\.c\.?|gmbh|ag|se|sa|plc)\b', '', company_normalized)
            company_normalized = re.sub(r'[^a-z0-9 ]+', '', company_normalized).strip()
            if not company_normalized:
                return False

            # Generate domain patterns for the cleaned company name
            base_patterns = [
                company_normalized.replace('&', 'and').replace(' ', ''),
                company_normalized.replace('&', 'and').replace(' ', '-'),
                company_normalized.replace('&', 'and').replace(' ', '_'),
            ]

            domain_extensions = ['.com', '.co.in', '.in', '.co.uk', '.co', '.io']
            domain_patterns = []
            for pattern in base_patterns:
                if pattern:
                    for ext in domain_extensions:
                        domain_patterns.append(pattern + ext)

            domain_patterns = list(dict.fromkeys(domain_patterns))

            # Try direct HTTPS and HTTP access patterns
            for domain in domain_patterns[:10]:
                for prefix in ['', 'www.']:
                    try:
                        url = f"https://{prefix}{domain}"
                        response = requests.head(url, timeout=5, allow_redirects=True)
                        if response.status_code < 400:
                            return True
                    except:
                        pass
                    try:
                        url = f"http://{prefix}{domain}"
                        response = requests.head(url, timeout=5, allow_redirects=True)
                        if response.status_code < 400:
                            return True
                    except:
                        pass

            # Method 2: Use Google Search API as fallback to identify official site
            if self.google_api_key and self.search_engine_id:
                search_query = f'"{company_normalized}" official website'
                search_results = self._google_search(search_query)
                if search_results and search_results.get('items'):
                    for item in search_results.get('items', [])[:6]:
                        url = item.get('link', '').lower()
                        title = item.get('title', '').lower()
                        snippet = item.get('snippet', '').lower() if item.get('snippet') else ''
                        if company_normalized in url or company_normalized in title or company_normalized in snippet:
                            if all(block not in url for block in ['linkedin.com', 'indeed.com', 'glassdoor.com', 'naukri.com']):
                                return True

            return False
        except Exception:
            return False

    def _check_linkedin_exists(self, company: str) -> bool:
        """Check if company has LinkedIn page using multiple methods"""
        try:
            company_clean = company.lower().strip()
            company_clean = re.sub(r'\b(pvt\.? ltd\.?|pvt\.?|ltd\.?|limited|inc\.?|corp\.?|corporation|co\.?|llc\.?|gmbh|ag|se|sa|plc)\b', '', company_clean)
            company_clean = re.sub(r'[^a-z0-9 ]+', '', company_clean).strip()
            if not company_clean:
                return False

            # Extended well-known companies list
            well_known_companies = [
                'google', 'microsoft', 'apple', 'amazon', 'facebook', 'meta', 'netflix',
                'tesla', 'twitter', 'linkedin', 'instagram', 'youtube', 'walmart',
                'coca cola', 'pepsi', 'nike', 'adidas', 'ibm', 'oracle', 'sap',
                'accenture', 'deloitte', 'pwc', 'ey', 'kpmg', 'mckinsey', 'goldman sachs',
                'jpmorgan', 'bank of america', 'wells fargo', 'cisco', 'intel', 'qualcomm',
                'broadcom', 'nvidia', 'amd', 'salesforce', 'adobe', 'vmware', 'workday',
                'servicenow', 'infosys', 'tcs', 'wipro', 'hcl', 'tech mahindra',
                'cognizant', 'mindtree', 'reliance', 'tata', 'mahindra', 'bajaj',
                'maruti', 'hero', 'hdfc', 'icici', 'sbi', 'axis bank', 'indigo',
                'flipkart', 'myntra', 'paytm', 'oyo', 'swiggy', 'zomato', 'ola',
                'bharti', 'jio', 'vodafone', 'siemens', 'bosch', 'ge', 'sony',
                'lg', 'samsung', 'hyundai', 'toyota', 'bmw', 'audi', 'mercedes', 'ford', 'gm',
                # Indian startups / mid-market
                'grabon', 'meesho', 'nykaa', 'razorpay', 'phonepe', 'cred', 'zepto',
                'blinkit', 'dunzo', 'moengage', 'freshworks', 'zoho', 'browserstack',
                'postman', 'hasura', 'cleartax', 'groww', 'upstox', 'smallcase',
                'urban company', 'urbanclap', 'lenskart', 'boat', 'mamaearth',
                'cars24', 'droom', 'spinny', 'classplus', 'unacademy', 'byju',
                'vedantu', 'doubtnut', 'physics wallah', 'testbook', 'learnyst',
                'slice', 'jupiter', 'fi money', 'niyo', 'mswipe', 'innovaccer',
                'darwinbox', 'keka', 'zoho recruit', 'hrms', 'springworks',
                'ather', 'ola electric', 'simple energy', 'ultraviolette',
                'healthkart', 'pharmeasy', 'netmeds', '1mg', 'practo', 'mfine'
            ]

            if any(known in company_clean for known in well_known_companies):
                return True

            company_variants = [
                company_clean,
                company_clean.replace(' ', '-'),
                company_clean.replace(' ', ''),
                company_clean.replace(' ', '_')
            ]
            company_variants = list(dict.fromkeys([variant for variant in company_variants if variant]))

            linkedin_urls = []
            for variant in company_variants[:8]:
                linkedin_urls.extend([
                    f"https://www.linkedin.com/company/{variant}",
                    f"https://www.linkedin.com/company/{variant}/",
                    f"https://www.linkedin.com/search/results/companies/?keywords={variant}",
                ])

            for url in linkedin_urls:
                try:
                    response = requests.get(url, timeout=6, allow_redirects=True, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    })
                    if response.status_code < 400:
                        url_lower = response.url.lower()
                        content = response.text.lower()
                        indicators = [
                            'linkedin.com/company' in url_lower,
                            'company page' in content,
                            'headquarters' in content,
                            'employees' in content,
                            'industry' in content,
                            'about' in content,
                        ]
                        if any(indicators):
                            return True
                except requests.exceptions.RequestException:
                    continue

            if self.google_api_key and self.search_engine_id:
                search_query = f'"{company_clean}" site:linkedin.com/company'
                search_results = self._google_search(search_query)
                if search_results and search_results.get('items'):
                    for item in search_results.get('items', [])[:5]:
                        url = item.get('link', '').lower()
                        title = item.get('title', '').lower()
                        snippet = item.get('snippet', '').lower() if item.get('snippet') else ''
                        if 'linkedin.com/company' in url and (company_clean in url or company_clean in title or company_clean in snippet):
                            return True

            return False

        except Exception as e:
            print(f"LinkedIn check error for {company}: {str(e)}")
            return False


class ScamDetectionAgent:
    """Agent 4: AI-powered scam detection using OpenAI"""

    def detect_scams(self, text: str) -> Dict:
        """Use OpenAI to detect scam patterns"""
        try:
            # Check if API key is available
            if not os.getenv('OPENAI_API_KEY'):
                print("⚠️  OpenAI API key not found - using fallback detection")
                return self._fallback_scam_detection(text)

            prompt = f"""Analyze this specific job posting for scam indicators. Provide a unique analysis based on the actual content of this posting.

Focus on:
1. Payment requirements (training fees, registration fees, etc.)
2. Unrealistic promises (guaranteed income, no experience needed, etc.)
3. Urgency tactics (immediate start, limited positions, etc.)
4. Suspicious contact methods
5. Red flags in job description

Job Posting:
{text}

IMPORTANT: Respond ONLY with valid JSON. No additional text.

JSON format:
{{
  "scam_score": 0-100,
  "detected_scams": ["list", "of", "scam", "patterns"],
  "risk_level": "Low|Medium|High|Critical",
  "explanation": "brief explanation"
}}"""

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )

            result_text = response.choices[0].message.content

            # Parse JSON response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                return self._fallback_scam_detection(text)

        except Exception as e:
            print(f"Scam detection error: {e}")
            error_msg = str(e)
            
            # Check if it's an API quota/billing error
            if "insufficient_quota" in error_msg.lower() or "429" in error_msg:
                return self._api_quota_exceeded_detection(text)
            
            return self._fallback_scam_detection(text)

    def _api_quota_exceeded_detection(self, text: str) -> Dict:
        """Fallback when OpenAI API quota is exceeded - uses enhanced rule-based detection"""
        text_lower = text.lower()
        detected_scams = []
        checked_signals = []

        # ── Payment / fee demands ─────────────────────────────────────────────
        payment_triggers = [
            "training fee", "registration fee", "application fee", "joining fee",
            "pay to work", "send money", "wire transfer", "western union",
            "upfront payment", "deposit required", "questionnaire fee",
            "processing fee", "pay before joining", "refundable deposit",
            "security deposit", "courier charges", "kit charges",
            "investment required", "buy materials", "purchase kit",
            "starter kit", "buy products", "initial investment",
            "money back", "cashback offer", "pay via upi", "pay via paytm",
        ]
        found_payment = [p for p in payment_triggers if p in text_lower]
        if found_payment:
            detected_scams.extend([f"Payment demand: '{p}'" for p in found_payment])
        checked_signals.append(f"Payment / fee demands: {'🚨 ' + str(len(found_payment)) + ' found' if found_payment else '✅ None detected'}")

        # ── Unrealistic income promises ───────────────────────────────────────
        income_triggers = [
            "guaranteed income", "earn ₹50,000", "earn ₹1,00,000", "earn 50000",
            "make money fast", "easy money", "get rich quick", "unlimited earning",
            "no experience required", "no qualification needed",
            "earn daily", "daily payout", "weekly payout", "instant payout",
            "₹500 per hour", "500 per hour", "1000 per day", "2000 per day",
            "earn from home", "lakhs per month", "crores", "passive income guaranteed",
        ]
        found_income = [p for p in income_triggers if p in text_lower]
        income_re = [r"\d{4,}\s*(per|/)\s*(day|week|hour)", r"earn\s+₹?\$?\d+", r"salary.*\d{5,}.*guarantee"]
        for pat in income_re:
            m = re.search(pat, text_lower)
            if m:
                found_income.append(m.group())
        if found_income:
            detected_scams.extend([f"Unrealistic income promise: '{p}'" for p in set(found_income)])
        checked_signals.append(f"Unrealistic income promises: {'🚨 ' + str(len(set(found_income))) + ' found' if found_income else '✅ None detected'}")

        # ── Urgency / pressure tactics ────────────────────────────────────────
        urgency_triggers = [
            "limited seats", "limited slots", "only few seats", "hurry",
            "last few positions", "closing soon", "apply immediately",
            "urgent hiring", "immediate joining", "joining today",
            "don't miss this opportunity", "act now", "respond asap",
            "vacancy closing", "interview today", "offer expires",
        ]
        found_urgency = [p for p in urgency_triggers if p in text_lower]
        if found_urgency:
            detected_scams.extend([f"Urgency / pressure tactic: '{p}'" for p in found_urgency])
        checked_signals.append(f"Urgency / pressure tactics: {'⚠️ ' + str(len(found_urgency)) + ' found' if found_urgency else '✅ None detected'}")

        # ── Vague / suspicious contact ────────────────────────────────────────
        contact_triggers = [
            "whatsapp only", "contact on whatsapp", "call on whatsapp",
            "no office address", "work from anywhere", "gmail.com recruiter",
            "yahoo.com recruiter", "no company email",
            "telegram", "contact via telegram",
        ]
        found_contact = [p for p in contact_triggers if p in text_lower]
        gmail_recruiter = bool(re.search(r'[\w.]+@(gmail|yahoo|hotmail|outlook)\.com', text_lower))
        if gmail_recruiter:
            found_contact.append("personal email domain used for recruitment")
        if found_contact:
            detected_scams.extend([f"Suspicious contact method: '{p}'" for p in found_contact])
        checked_signals.append(f"Suspicious contact / email: {'⚠️ ' + str(len(found_contact)) + ' found' if found_contact else '✅ None detected'}")

        # ── Grammar / vagueness signals ───────────────────────────────────────
        vague_triggers = [
            "kindly revert", "do the needful", "revert back asap",
            "good communication skill", "basic computer knowledge",
            "no experience needed", "fresher can apply", "any graduate",
            "12th pass", "10th pass", "work from home no experience",
        ]
        found_vague = [p for p in vague_triggers if p in text_lower]
        checked_signals.append(f"Vague / low-bar requirements: {'⚠️ ' + str(len(found_vague)) + ' found' if found_vague else '✅ None detected'}")

        # ── Positive / legitimate signals ─────────────────────────────────────
        legit_signals = []
        if re.search(r'(pvt\.?\s*ltd|private limited|inc\.|corporation|llp)', text_lower):
            legit_signals.append("Registered company name format present")
        if re.search(r'(glassdoor|linkedin|naukri|indeed|internshala)', text_lower):
            legit_signals.append("References a known job platform")
        if re.search(r'(benefits|health insurance|pf|provident fund|esi|gratuity)', text_lower):
            legit_signals.append("Mentions standard employee benefits")
        if re.search(r'(interview process|technical round|hr round|assessment)', text_lower):
            legit_signals.append("Describes structured interview process")
        if re.search(r'(notice period|background check|offer letter|appointment letter)', text_lower):
            legit_signals.append("Mentions legitimate HR processes")
        checked_signals.append(f"Legitimate signals found: {', '.join(legit_signals) if legit_signals else 'None detected — posting may lack standard legitimacy markers'}")

        all_detected = list(set(detected_scams))
        scam_score = min(len(all_detected) * 12, 100)
        if found_vague:
            scam_score = min(scam_score + len(found_vague) * 5, 100)
        if legit_signals:
            scam_score = max(scam_score - len(legit_signals) * 8, 0)

        risk_level = "Low"
        if scam_score >= 70: risk_level = "High"
        elif scam_score >= 35: risk_level = "Medium"

        explanation_parts = [
            f"Rule-based analysis checked {len(checked_signals)} signal categories:",
            *[f"  • {s}" for s in checked_signals],
        ]
        if all_detected:
            explanation_parts.append(f"Total suspicious signals: {len(all_detected)}")
        if legit_signals:
            explanation_parts.append(f"Legitimacy indicators reduced the score by {len(legit_signals) * 8}%")
        if not all_detected and not legit_signals:
            explanation_parts.append("No clear scam indicators OR strong legitimacy signals found. Recommend verifying company via LinkedIn and official website.")

        return {
            "scam_score": scam_score,
            "detected_scams": all_detected,
            "risk_level": risk_level,
            "explanation": " | ".join(explanation_parts),
            "checked_signals": checked_signals,
            "legit_signals": legit_signals,
        }

    def _fallback_scam_detection(self, text: str) -> Dict:
        """Fallback scam detection using rule-based approach"""
        text_lower = text.lower()
        scam_indicators = [
            "training fee", "registration fee", "application fee",
            "pay to work", "send money", "wire transfer",
            "guaranteed income", "earn ₹50,000/week", "make money fast",
            "upfront payment", "deposit required", "questionnaire fee",
            "work from home no experience", "easy money", "get rich quick",
            "investment required", "buy materials", "processing fee",
            "pay before joining", "refundable deposit", "security deposit"
        ]

        detected_scams = [indicator for indicator in scam_indicators if indicator in text_lower]

        scam_score = min(len(detected_scams) * 20, 100)

        risk_level = "Low"
        if scam_score >= 80: risk_level = "Critical"
        elif scam_score >= 60: risk_level = "High"
        elif scam_score >= 40: risk_level = "Medium"

        return {
            "scam_score": scam_score,
            "detected_scams": detected_scams,
            "risk_level": risk_level,
            "explanation": f"Found {len(detected_scams)} scam indicators"
        }


class DecisionAgent:
    """Agent 5: Combines all agent results to make final decision"""

    def decide(self, extractor_result: Dict, search_result: Dict,
               verification_result: Dict, scam_result: Dict, ml_result: Dict = None) -> Dict:
        """Combine all agent results for final risk assessment"""

        ml_result = ml_result or {}

        # Calculate weighted scores with adaptive weighting
        company_verified = (verification_result.get("website_exists", False) or 
                           verification_result.get("linkedin_exists", False))

        weights = {
            "search_confidence": 0.20,
            "verification_score": 0.25,
            "scam_score": 0.25,
            "ml_fake_probability": 0.20,
            "extraction_confidence": 0.10
        }

        normalized_scores = {
            "search_confidence": search_result.get("confidence_score", 0),
            "verification_score": verification_result.get("verification_score", 0),
            "scam_score": scam_result.get("scam_score", 0) / 100.0,
            "ml_fake_probability": ml_result.get("ml_fake_probability", 0),
            "extraction_confidence": extractor_result.get("extraction_confidence", 0)
        }

        final_risk_score = (
            (1 - normalized_scores["search_confidence"]) * weights["search_confidence"] +
            (1 - normalized_scores["verification_score"]) * weights["verification_score"] +
            normalized_scores["scam_score"] * weights["scam_score"] +
            normalized_scores["ml_fake_probability"] * weights["ml_fake_probability"] +
            (1 - normalized_scores["extraction_confidence"]) * weights["extraction_confidence"]
        )

        if company_verified and final_risk_score < 0.7:
            final_risk_score *= 0.82

        final_risk_score = min(max(final_risk_score, 0), 1.0)

        # Determine risk level with adjusted thresholds
        if company_verified and final_risk_score < 0.55:
            if final_risk_score >= 0.4:
                risk_level = "Medium"
                recommendation = "⚠️ MEDIUM RISK - Company verified but review details carefully"
            else:
                risk_level = "Low"
                recommendation = "✅ LOW RISK - Appears legitimate"
        elif final_risk_score >= 0.75:
            risk_level = "High"
            recommendation = "🚨 HIGH RISK - Likely a scam"
        elif final_risk_score >= 0.5:
            risk_level = "Medium"
            recommendation = "⚠️ MEDIUM RISK - Exercise caution"
        else:
            risk_level = "Low"
            recommendation = "✅ LOW RISK - Appears legitimate"

        # Generate explanation
        explanation_parts = []

        # Search results explanation
        platforms_found = search_result.get("found_on_platforms", [])
        if platforms_found:
            explanation_parts.append(f"Found on {len(platforms_found)} platform(s): {', '.join(platforms_found)}")
        else:
            explanation_parts.append("Direct company recruitment (not on mainstream platforms - normal for campus drives)")

        # Company verification explanation
        if verification_result.get("website_exists"):
            explanation_parts.append("✅ Company website verified")
        else:
            explanation_parts.append("❌ No company website found")

        if verification_result.get("linkedin_exists"):
            explanation_parts.append("✅ LinkedIn company page verified")
        else:
            explanation_parts.append("❌ No LinkedIn company page found")

        # Scam detection explanation
        scam_score = scam_result.get("scam_score", 0)
        if scam_score >= 60:
            explanation_parts.append(f"⚠️ AI detected {len(scam_result.get('detected_scams', []))} scam patterns")
        elif scam_score >= 30:
            explanation_parts.append("⚠️ Some suspicious patterns detected")
        else:
            explanation_parts.append("✅ No major scam indicators found")

        if ml_result.get("ml_available"):
            explanation_parts.append(f"🤖 ML model estimated fake probability at {round(normalized_scores['ml_fake_probability'] * 100, 1)}%")
        else:
            explanation_parts.append("🤖 ML model unavailable; using fallback scoring.")

        return {
            "final_risk_score": round(final_risk_score * 100, 1),
            "risk_level": risk_level,
            "recommendation": recommendation,
            "explanation": " | ".join(explanation_parts),
            "confidence_breakdown": {
                "cross_platform_search": round(normalized_scores["search_confidence"] * 100, 1),
                "company_verification": round(normalized_scores["verification_score"] * 100, 1),
                "scam_detection": round(normalized_scores["scam_score"] * 100, 1),
                "ml_fake_probability": round(normalized_scores["ml_fake_probability"] * 100, 1),
                "data_quality": round(normalized_scores["extraction_confidence"] * 100, 1),
                "company_verified": company_verified
            },
            "agent_results": {
                "extractor": extractor_result,
                "search": search_result,
                "verification": verification_result,
                "scam_detection": scam_result,
                "ml_analysis": ml_result
            }
        }


class MultiAgentFakeJobDetector:
    """Main orchestrator for the multi-agent fake job detection system"""

    def __init__(self):
        self.extractor = JobExtractorAgent()
        self.search_agent = CrossPlatformSearchAgent()
        self.verification_agent = CompanyVerificationAgent()
        self.scam_detector = ScamDetectionAgent()
        self.decision_agent = DecisionAgent()

    def detect(self, text: str) -> Dict:
        """Run the complete multi-agent detection pipeline"""

        # Agent 1: Extract job information
        extraction_result = self.extractor.extract(text)

        # Agent 2: Cross-platform search
        search_result = self.search_agent.search(
            extraction_result["company"],
            extraction_result["role"]
        )

        # Agent 3: Company verification
        verification_result = self.verification_agent.verify(
            extraction_result["company"]
        )

        # Agent 4: Scam detection
        scam_result = self.scam_detector.detect_scams(text)

        # Agent 5: Final decision
        final_result = self.decision_agent.decide(
            extraction_result,
            search_result,
            verification_result,
            scam_result
        )

        return final_result


class ResumeJobMatchAgent:
    """Agent 6: Analyzes resume-job fit using AI"""

    def analyze_match(self, resume_text: str, job_text: str) -> Dict:
        """Analyze how well a resume matches a job posting"""
        try:
            if not os.getenv('OPENAI_API_KEY'):
                return self._fallback_match_analysis(resume_text, job_text)

            prompt = f"""Analyze how well this resume matches this job posting. Consider:

1. Skills match (technical skills, experience level)
2. Experience relevance (years, industry, role type)
3. Education requirements vs qualifications
4. Key responsibilities alignment
5. Missing critical requirements

Resume:
{resume_text[:2000]}

Job Posting:
{job_text[:2000]}

Respond with JSON containing:
- match_score: 0-100 (100 = perfect match)
- match_level: "Poor", "Fair", "Good", "Excellent"
- skills_match: percentage of required skills present
- experience_match: "Underqualified", "Qualified", "Overqualified"
- missing_requirements: list of key missing items
- recommendations: suggestions for improvement"""

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.2
            )

            result_text = response.choices[0].message.content

            # Parse JSON response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                return self._fallback_match_analysis(resume_text, job_text)

        except Exception as e:
            print(f"Resume-job match error: {e}")
            error_msg = str(e)
            
            # Check if it's an API quota/billing error
            if "insufficient_quota" in error_msg.lower() or "429" in error_msg:
                return self._api_quota_exceeded(resume_text, job_text)
            
            return self._fallback_match_analysis(resume_text, job_text)

    def _api_quota_exceeded(self, resume_text: str, job_text: str) -> Dict:
        """Fallback when OpenAI API quota is exceeded"""
        # Perform basic keyword matching
        resume_lower = resume_text.lower()
        job_lower = job_text.lower()

        # Extract potential skills from job
        job_words = set(re.findall(r'\b\w+\b', job_lower))
        resume_words = set(re.findall(r'\b\w+\b', resume_lower))

        # Simple overlap calculation
        common_words = job_words.intersection(resume_words)
        match_score = min(len(common_words) * 2, 100)

        match_level = "Poor"
        if match_score >= 80: match_level = "Excellent"
        elif match_score >= 60: match_level = "Good"
        elif match_score >= 40: match_level = "Fair"

        return {
            "match_score": match_score,
            "match_level": match_level,
            "skills_match": match_score,
            "experience_match": "Unknown - API quota exceeded",
            "missing_requirements": ["OpenAI API quota exceeded"],
            "recommendations": [
                "Check OpenAI billing: https://platform.openai.com/account/billing/limits",
                "Or upgrade to a paid OpenAI plan",
                "Using basic keyword matching for now"
            ]
        }

    def _fallback_match_analysis(self, resume_text: str, job_text: str) -> Dict:
        """Basic keyword-based matching as fallback"""
        resume_lower = resume_text.lower()
        job_lower = job_text.lower()

        # Extract potential skills from job
        job_words = set(re.findall(r'\b\w+\b', job_lower))
        resume_words = set(re.findall(r'\b\w+\b', resume_lower))

        # Simple overlap calculation
        common_words = job_words.intersection(resume_words)
        match_score = min(len(common_words) * 2, 100)

        match_level = "Poor"
        if match_score >= 80: match_level = "Excellent"
        elif match_score >= 60: match_level = "Good"
        elif match_score >= 40: match_level = "Fair"

        return {
            "match_score": match_score,
            "match_level": match_level,
            "skills_match": match_score,
            "experience_match": "Unknown",
            "missing_requirements": ["Detailed analysis requires OpenAI API"],
            "recommendations": ["Configure OpenAI API key in .env file for advanced analysis"]
        }
