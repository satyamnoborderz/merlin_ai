# app/services/score_calculator.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.utils.logger import setup_logger

logger = setup_logger()

class ScoreCalculator:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    def calculate_job_title_score(self, resume_title: str, job_title: str) -> float:
        if not resume_title or not job_title:
            return 0.0

        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of'}
        resume_tokens = [word.lower() for word in resume_title.split() if word.lower() not in stop_words]
        job_tokens = [word.lower() for word in job_title.split() if word.lower() not in stop_words]

        if not resume_tokens or not job_tokens:
            return 0.0

        resume_set = set(resume_tokens)
        job_set = set(job_tokens)
        jaccard_similarity = len(resume_set.intersection(job_set)) / len(resume_set.union(job_set))

        resume_embedding = self.model.encode(resume_title)
        job_embedding = self.model.encode(job_title)
        embedding_similarity = cosine_similarity([resume_embedding], [job_embedding])[0][0]

        return (jaccard_similarity + embedding_similarity) / 2

    def calculate_skills_score(self, resume_skills: list, job_skills: list) -> float:
        if not job_skills:
            return 1.0

        resume_skills_set = set(''.join(skill.lower().split()) for skill in resume_skills)
        job_skills_set = set(''.join(skill.lower().split()) for skill in job_skills)

        exact_matches = resume_skills_set.intersection(job_skills_set)
        exact_match_score = len(exact_matches) / len(job_skills_set)

        resume_embeddings = self.model.encode(list(resume_skills_set))
        job_embeddings = self.model.encode(list(job_skills_set))

        if len(resume_embeddings) > 0 and len(job_embeddings) > 0:
            similarities = cosine_similarity(resume_embeddings, job_embeddings)
            semantic_score = np.mean(np.max(similarities, axis=0))
        else:
            semantic_score = 0

        return (exact_match_score + semantic_score) / 2

    # [Additional scoring methods...]
    # Note: Include other scoring methods from the original code

    def normalize_education(self,edu):
            edu = edu.lower().replace("'s", "").replace("'", "")
            if "high school" in edu or "ged" in edu:
                return "high school"
            elif "associate" in edu or "aa" in edu or "as" in edu:
                return "associate"
            elif "bachelor" in edu or "ba" in edu or "bs" in edu:
                return "bachelor"
            elif "master" in edu or "ma" in edu or "ms" in edu or "mba" in edu:
                return "master"
            elif "phd" in edu or "doctorate" in edu or "doctoral" in edu:
                return "phd"
            else:
                return edu



    def calculate_education_score(self,resume_edu, job_edu):
        logger.info(f"Calculating education score for {resume_edu} against {job_edu}")
        edu_levels = {'high school': 1, 'associate': 2, 'bachelor': 3, 'master': 4, 'phd': 5}
        
        normalized_resume_edu = [self.normalize_education(edu) for edu in resume_edu]
        normalized_job_edu = [self.normalize_education(edu) for edu in job_edu]
        
        resume_level = max((edu_levels.get(edu, 0) for edu in normalized_resume_edu), default=0)
        job_level = max((edu_levels.get(edu, 0) for edu in normalized_job_edu), default=0)
        
        if job_level == 0:
            return 1.0
        
        score = min(resume_level / job_level, 1.0)
        logger.info(f"Education score: {score}")
        return score






    def calculate_experience_score(self,resume_years, job_years):
        logger.info(f"Calculating experience score for {resume_years} years against {job_years} years")
        if job_years == 0:
            return 1.0
        
        score = min(resume_years / job_years, 1.0)
        logger.info(f"Experience score: {score}")
        return score

    def calculate_category_score(self,resume_items, job_items):
        logger.info(f"Calculating category score for {resume_items} against {job_items}")
        if not job_items:
            return 1.0
        match_count = len(set(resume_items) & set(job_items))
        score = match_count / len(job_items)
        logger.info(f"Category score: {score}")
        return score

    def similarty_score(self,resume_text,job_description):
        resume_embedding = self.model.encode(resume_text)
        job_embedding = self.model.encode(job_description)
        embedding_similarity = cosine_similarity([resume_embedding], [job_embedding])[0][0]
        return embedding_similarity
   





 