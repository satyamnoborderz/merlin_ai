# app/services/text_processor.py


import re
import spacy
import yake
from collections import defaultdict
from typing import Dict, Set, Union, List
from app.utils.logger import setup_logger

logger = setup_logger()

class TextProcessor:
    def __init__(self):
        """Initialize the TextProcessor with required NLP models."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.keyword_extractor = yake.KeywordExtractor(
                lan="en", 
                n=3, 
                dedupLim=0.9, 
                top=20, 
                features=None
            )
        except Exception as e:
            logger.error(f"Failed to initialize TextProcessor: {str(e)}")
            raise

    def extract_categories(self, text: str) -> Dict[str, Union[Set[str], int]]:
        """
        Extract all categories from the given text.
        
        Args:
            text (str): Input text to process
            
        Returns:
            Dict[str, Union[Set[str], int]]: Dictionary containing extracted categories
        """
        logger.info("Extracting categories from text")
        doc = self.nlp(text)
        categories = defaultdict(set)

        self._extract_job_title(text, categories, doc)
        self._extract_skills(text, categories)
        self._extract_entities(doc, categories)
        self._extract_education(text, categories)
        self._extract_experience_level(text, categories)
        self._extract_job_type(text, categories)
        self._extract_industry(text, categories)
        self._extract_years_experience(text, categories)

        return dict(categories)

    def extract_info(self, text: str, categories: Dict[str, Union[Set[str], int]]) -> Dict[str, Union[List[str], int]]:
        """
        Extract specific information based on predefined categories.
        
        Args:
            text (str): Input text to process
            categories (Dict[str, Union[Set[str], int]]): Categories to extract
            
        Returns:
            Dict[str, Union[List[str], int]]: Extracted information
        """
        logger.info("Extracting information from text")
        info = {category: [] for category in categories}
        
        keywords = self.keyword_extractor.extract_keywords(text)
        extracted_keywords = set(keyword[0].lower() for keyword in keywords)
        
        for category, items in categories.items():
            if isinstance(items, set):
                for item in items:
                    if item in extracted_keywords or re.search(r'\b' + re.escape(item) + r'\b', text, re.IGNORECASE):
                        info[category].append(item.lower())
            elif category == "years_of_experience":
                years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
                years_match = re.search(years_pattern, text, re.IGNORECASE)
                info[category] = int(years_match.group(1)) if years_match else 0
        
        logger.info(f"Extracted information: {info}")
        return info

    def _extract_job_title(self, text: str, categories: defaultdict, doc) -> None:
        """Extract job title from text using various patterns."""
        job_title_patterns = [
            r"(?i)(?:job title|position|role|title|position title|job role)s?:?\s*(.*?)(?:\n|$)",
            r"(?i)(?:we are hiring|hiring for|looking for|seeking)\s*(?:a|an)?\s*(.*?)(?:\n|$)",
            r"(?i)^(?:senior|junior|lead|principal|staff)?\s*([^.!?\n]+)(?:\n|$)"
        ]
        
        for pattern in job_title_patterns:
            job_title_match = re.search(pattern, text)
            if job_title_match:
                categories["job_title"].add(job_title_match.group(1).strip().lower())
                return

        # Fallback to first sentence if no matches found
        if not categories["job_title"] and len(list(doc.sents)) > 0:
            first_sentence = next(doc.sents).text
            categories["job_title"].add(first_sentence.strip().lower())

    def _extract_skills(self, text: str, categories: defaultdict) -> None:
        """Extract skills using keyword extraction and pattern matching."""
        # Extract keywords using YAKE
        keywords = self.keyword_extractor.extract_keywords(text)
        categories["skills"].update(keyword[0].lower() for keyword in keywords)

        # Additional skill patterns
        skill_patterns = [
            r'\b(?:proficient|experienced|skilled|expertise)\s+in\s+([\w\s,/+]+)',
            r'\b(?:knowledge|understanding)\s+of\s+([\w\s,/+]+)',
            r'(?:technologies|tools|frameworks|languages):\s*([\w\s,/+]+)',
            r'\b(?:HTML5?|CSS3?|JavaScript|Python|Java|C\+\+|React|Angular|Vue|Node\.js|SQL|AWS|Azure|Git)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    skills = match.group(1).split(',')
                    categories["skills"].update(skill.strip().lower() for skill in skills)
                else:
                    categories["skills"].add(match.group(0).lower())

    def _extract_entities(self, doc, categories: defaultdict) -> None:
        """Extract named entities from the document."""
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT"]:
                categories["skills"].add(ent.text.lower())
            elif ent.label_ == "GPE":
                categories["location"].add(ent.text.lower())

    def _extract_education(self, text: str, categories: defaultdict) -> None:
        """Extract education requirements from text."""
        education_patterns = [
            r'\b(?:high school diploma|GED|secondary education)\b',
            r'\b(?:associate\'?s?|AA|AS)\s*(?:degree)?\b',
            r'\b(?:bachelor\'?s?|BA|BS|B\.A\.|B\.S\.)\s*(?:degree)?\b',
            r'\b(?:master\'?s?|MA|MS|M\.A\.|M\.S\.|MBA|M\.B\.A\.)\s*(?:degree)?\b',
            r'\b(?:phd|ph\.d\.|doctorate|doctoral)\s*(?:degree)?\b',
            r'\b(?:post-graduate|postgraduate)\s*(?:degree|qualification)?\b'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            categories["education"].update(match.lower() for match in matches)

    def _extract_experience_level(self, text: str, categories: defaultdict) -> None:
        """Extract experience level requirements from text."""
        experience_patterns = [
            r'\b(?:entry[ -]level|junior|graduate|fresher)\b',
            r'\b(?:mid[ -]level|intermediate|associate)\b',
            r'\b(?:senior|experienced|advanced)\b',
            r'\b(?:lead|principal|architect|manager)\b',
            r'\b(?:director|head|chief|vp|vice president|executive)\b',
            r'\b(?:c-level|cto|cio|ceo|cfo)\b'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            categories["experience"].update(match.lower() for match in matches)

    def _extract_job_type(self, text: str, categories: defaultdict) -> None:
        """Extract job type information from text."""
        job_type_patterns = [
            r'\b(?:full[ -]time|permanent|regular)\b',
            r'\b(?:part[ -]time|hourly)\b',
            r'\b(?:contract|temporary|interim|temp)\b',
            r'\b(?:freelance|independent|consultant)\b',
            r'\b(?:internship|intern|trainee|co-op)\b',
            r'\b(?:remote|work from home|wfh|hybrid|on-site|in-office)\b'
        ]
        
        for pattern in job_type_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            categories["job_type"].update(match.lower() for match in matches)

    def _extract_industry(self, text: str, categories: defaultdict) -> None:
        """Extract industry information from text."""
        industry_patterns = [
            r'\b(?:technology|IT|software|tech)\b',
            r'\b(?:finance|banking|fintech|insurance)\b',
            r'\b(?:healthcare|medical|pharma|biotech)\b',
            r'\b(?:education|academic|e-learning)\b',
            r'\b(?:retail|e-commerce|consumer)\b',
            r'\b(?:manufacturing|industrial|production)\b',
            r'\b(?:media|entertainment|digital|creative)\b',
            r'\b(?:government|public sector|defense)\b',
            r'\b(?:consulting|professional services)\b',
            r'\b(?:telecommunications|telecom)\b',
            r'\b(?:automotive|transportation)\b',
            r'\b(?:energy|utilities|oil|gas)\b'
        ]
        
        for pattern in industry_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            categories["industry"].update(match.lower() for match in matches)

    def _extract_years_experience(self, text: str, categories: defaultdict) -> None:
        """Extract years of experience requirements from text."""
        years_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
            r'(?:minimum|min)\s*(?:of)?\s*(\d+)\s*(?:years?|yrs?)',
            r'(?:at least|minimum)\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)(?:-\d+)?\s*(?:years?|yrs?)\s*(?:experience|exp)?'
        ]
        
        max_years = 0
        for pattern in years_patterns:
            years_match = re.search(pattern, text, re.IGNORECASE)
            if years_match:
                years = int(years_match.group(1))
                max_years = max(max_years, years)
        
        if max_years > 0:
            categories["years_of_experience"] = max_years

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text by cleaning and normalizing it.
        
        Args:
            text (str): Input text to process
            
        Returns:
            str: Preprocessed text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep relevant ones
        text = re.sub(r'[^a-zA-Z0-9\s\.\+#/\-]', '', text)
        
        return text

    def extract_specific_category(self, text: str, category: str) -> Set[str]:
        """
        Extract information for a specific category from text.
        
        Args:
            text (str): Input text to process
            category (str): Category to extract
            
        Returns:
            Set[str]: Extracted items for the specified category
        """
        categories = self.extract_categories(text)
        return categories.get(category, set())

    def merge_categories(self, categories1: Dict[str, Set[str]], 
                        categories2: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """
        Merge two category dictionaries.
        
        Args:
            categories1 (Dict[str, Set[str]]): First category dictionary
            categories2 (Dict[str, Set[str]]): Second category dictionary
            
        Returns:
            Dict[str, Set[str]]: Merged categories
        """
        merged = defaultdict(set)
        for category in set(categories1.keys()) | set(categories2.keys()):
            merged[category] = categories1.get(category, set()) | categories2.get(category, set())
        return dict(merged)