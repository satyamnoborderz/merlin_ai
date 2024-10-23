# app/services/ats_calculator.py
from app.services.text_processor import TextProcessor
from app.services.score_calculator import ScoreCalculator
from app.utils.logger import setup_logger

logger = setup_logger()

class ATSCalculator:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.score_calculator = ScoreCalculator()
        self.weights = {
            'job_title': 0.15,
            'skills': 0.30,
            'education': 0.10,
            'experience': 0.10,
            'years_of_experience': 0.10,
            'industry': 0.05,
            'job_type': 0.05,
            'location': 0.05,
            'text_similarity': 0.10
        }

    def calculate_ats_score(self, resume_text: str, job_description: str):
        categories = self.text_processor.extract_categories(job_description)
        resume_info = self.text_processor.extract_info(resume_text, categories)
        job_info = self.text_processor.extract_info(job_description, categories)
        similar_score=self.score_calculator.similarty_score(resume_text,job_description)
        
        scores = self._calculate_category_scores(resume_info, job_info)
        scores['text_similarity']=similar_score
        
        total_score = self._calculate_total_score(scores)

        
        return total_score * 100, scores, resume_info, job_info

    def _calculate_category_scores(self, resume_info, job_info):
        scores = {}
        for category in job_info:
            try:
                if category == 'education':
                    scores[category] = self.score_calculator.calculate_education_score(
                        resume_info[category], job_info[category]
                    )
                elif category == 'years_of_experience':
                    scores[category] = self.score_calculator.calculate_experience_score(
                        resume_info[category], job_info[category]
                    )
                elif category == 'job_title':
                    resume_title = ' '.join(resume_info[category])
                    job_title = ' '.join(job_info[category])
                    scores[category] = self.score_calculator.calculate_job_title_score(
                        resume_title, job_title
                    )
                elif category == 'skills':
                    scores[category] = self.score_calculator.calculate_skills_score(
                        resume_info[category], job_info[category]
                    )
               

                else:
                    scores[category] = self.score_calculator.calculate_category_score(
                        resume_info[category], job_info[category]
                    )
            except Exception as e:
                logger.error(f"Error calculating score for {category}: {str(e)}")
                scores[category] = 0.0

        return scores

    def _calculate_total_score(self, scores):
        kk =sum(scores.get(category, 0) * weight 
                  for category, weight in self.weights.items())

        return kk

  
    





    def provide_feedback(self,score, category_scores, resume_info, job_info):
        logger.info("Providing feedback based on the ATS score")
        feedback = []
        
        if score < 70:
            feedback.append("Your overall match with the job requirements needs improvement.")
        elif score < 85:
            feedback.append("You have a good match with the job requirements, but there's room for improvement.")
        else:
            feedback.append("Excellent match with the job requirements!")
        
        if 'job_title' in resume_info and 'job_title' in job_info:
            resume_title = ' '.join(resume_info['job_title'])
            job_title = ' '.join(job_info['job_title'])
            title_score = category_scores['job_title']
            if title_score < 0.5:
                feedback.append(f"Your resume title '{resume_title}' doesn't closely match the job title '{job_title}'. Consider aligning your resume title more closely with the job title.")
        
        for category in job_info:
            if category not in ['years_of_experience', 'job_title']:
                missing_items = set(job_info[category]) - set(resume_info[category])
                if missing_items:
                    feedback.append(f"Consider adding or highlighting these {category}: {', '.join(missing_items)}.")
        
        if 'years_of_experience' in resume_info and 'years_of_experience' in job_info:
            if resume_info['years_of_experience'] < job_info['years_of_experience']:
                feedback.append(f"The job requires {job_info['years_of_experience']} years of experience, but your resume shows {resume_info['years_of_experience']} years.")
        
        logger.info(f"Feedback generated: {feedback}")
        return "\n".join(feedback)