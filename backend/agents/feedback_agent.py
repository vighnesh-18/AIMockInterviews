from crewai import Agent, Task
import os

GROQ_API_KEY = os.getenv('GROQ_API_KEY_4')

class FeedbackAgent:
    def __init__(self):
        self.agent = Agent(
            role='Interview Report Generator',
            goal='Generate comprehensive final interview reports',
            backstory='Expert at synthesizing interview data',
            verbose=True,
            allow_delegation=False,
            llm='groq/llama-3.1-8b-instant'
        )
    
    def create_report_task(self, role, experience, difficulty, interaction_blocks, topics_covered, average_score):
        task = Task(
            description=f'Generate final interview report for {role} role',
            expected_output='JSON with interview report',
            agent=self.agent
        )
        return task
