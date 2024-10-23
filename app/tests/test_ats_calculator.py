




jd ="""job title: Marketing Coordinator
Company: XYZ Corp
Location: New York, NY
Job Type: Full-Time

Job Summary:
XYZ Corp is seeking a Marketing Coordinator to assist in the development and execution of marketing campaigns. The ideal candidate will be creative, detail-oriented, and passionate about brand management.

Key Responsibilities:

Assist in the planning and execution of marketing strategies.
Coordinate social media campaigns across various platforms.
Conduct market research to identify new opportunities.
Collaborate with graphic designers to create marketing materials.
Analyze campaign performance metrics and report findings.
Support the marketing team in daily administrative tasks.
Qualifications:

Bachelor’s degree in Marketing, Business, or related field.
1-2 years of experience in marketing or communications.
Proficient in Microsoft Office Suite and social media platforms.
Strong communication and organizational skills.
Ability to work independently and as part of a team.."""



resue="""John Doe
123 Main St.
New York, NY 10001
(123) 456-7890
johndoe@email.com

Objective
Enthusiastic Marketing Coordinator with over two years of experience in Marketing Coordinator and project management. Seeking to leverage skills in campaign execution and market research to contribute to the dynamic team at XYZ Corp.

Education
Bachelor of Arts in Marketing
University of New York, New York, NY
Graduated: May 2021

Experience

Marketing Assistant
ABC Marketing Agency, New York, NY
June 2021 – Present

Assisted in the development of multi-channel marketing campaigns, increasing client engagement by 30%.
Managed social media accounts, resulting in a 25% increase in followers over six months.
Conducted market research and competitor analysis, providing insights that influenced marketing strategies.
Intern
Creative Solutions, New York, NY
January 2021 – May 2021

Supported the marketing team with the execution of promotional events and product launches.
Created content for newsletters and social media posts, improving open rates by 15%.
Assisted in administrative tasks, ensuring smooth day-to-day operations.
Skills

Social Media Management (Facebook, Instagram, LinkedIn)
Data Analysis (Google Analytics, Excel)
Content Creation (Blogging, Copywriting)
Project Management (Trello, Asana)
Microsoft Office Suite (Word, PowerPoint, Excel)
Certifications

Google Analytics Certified
HubSpot Content Marketing Certification"""
















import requests

url = 'http://127.0.0.1:8000/calculate-ats-score'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}
data = {
    "job_description": jd,
    "resume": resue
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Error:", response.status_code, response.text)
