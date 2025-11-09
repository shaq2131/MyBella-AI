"""
Create exercise tracking tables
Run this once to add exercises support to MyBella
"""

from backend import create_app
from backend.database.models.models import db
from backend.database.models.exercise_models import ExerciseCompletion, JournalingPrompt

def create_exercise_tables():
    """Create exercise tables in database"""
    app, _ = create_app()
    
    with app.app_context():
        print("Creating exercise tables...")
        
        # Create tables
        db.create_all()
        
        print("Exercise tables created successfully!")
        
        # Seed journaling prompts
        seed_journaling_prompts()
        
        print("\n All done! Exercise system is ready.")


def seed_journaling_prompts():
    """Seed database with journaling prompts"""
    
    # Check if prompts already exist
    existing_count = JournalingPrompt.query.count()
    if existing_count > 0:
        print(f"Found {existing_count} existing journaling prompts. Skipping seed.")
        return
    
    print("Seeding journaling prompts...")
    
    prompts = [
        # Gratitude
        {
            'category': 'gratitude',
            'prompt': 'What are three things you are grateful for today, and why do they matter to you?',
            'difficulty': 'beginner',
            'tags': 'gratitude,positivity,reflection'
        },
        {
            'category': 'gratitude',
            'prompt': 'Describe a person in your life you appreciate. What have they done that made an impact on you?',
            'difficulty': 'beginner',
            'tags': 'gratitude,relationships,appreciation'
        },
        {
            'category': 'gratitude',
            'prompt': 'What small, everyday moments bring you joy? How can you create more of them?',
            'difficulty': 'intermediate',
            'tags': 'gratitude,joy,mindfulness'
        },
        
        # Reflection
        {
            'category': 'reflection',
            'prompt': 'What was the most challenging part of your day? How did you handle it?',
            'difficulty': 'beginner',
            'tags': 'reflection,challenges,growth'
        },
        {
            'category': 'reflection',
            'prompt': 'If you could redo one moment from today, what would it be and what would you do differently?',
            'difficulty': 'intermediate',
            'tags': 'reflection,learning,improvement'
        },
        {
            'category': 'reflection',
            'prompt': 'What emotions did you experience today? What triggered them?',
            'difficulty': 'intermediate',
            'tags': 'reflection,emotions,awareness'
        },
        {
            'category': 'reflection',
            'prompt': 'Looking back at the past week, what patterns do you notice in your thoughts or behaviors?',
            'difficulty': 'advanced',
            'tags': 'reflection,patterns,self-awareness'
        },
        
        # Goals
        {
            'category': 'goals',
            'prompt': 'What is one goal you want to accomplish this week? What small step can you take today?',
            'difficulty': 'beginner',
            'tags': 'goals,planning,action'
        },
        {
            'category': 'goals',
            'prompt': 'What obstacles are preventing you from reaching your goals? How can you overcome them?',
            'difficulty': 'intermediate',
            'tags': 'goals,obstacles,problem-solving'
        },
        {
            'category': 'goals',
            'prompt': 'Imagine your ideal self one year from now. What habits would they have that you don\'t have yet?',
            'difficulty': 'intermediate',
            'tags': 'goals,vision,habits'
        },
        
        # Anxiety
        {
            'category': 'anxiety',
            'prompt': 'What is worrying you right now? Write it all down, then identify what is within your control.',
            'difficulty': 'beginner',
            'tags': 'anxiety,worry,control'
        },
        {
            'category': 'anxiety',
            'prompt': 'When you feel anxious, what physical sensations do you notice? How can you soothe your body?',
            'difficulty': 'intermediate',
            'tags': 'anxiety,body,coping'
        },
        {
            'category': 'anxiety',
            'prompt': 'What would you tell a friend who was experiencing the same anxiety you are feeling?',
            'difficulty': 'intermediate',
            'tags': 'anxiety,compassion,perspective'
        },
        {
            'category': 'anxiety',
            'prompt': 'What is the worst-case scenario you\'re imagining? Now, what is the most likely realistic outcome?',
            'difficulty': 'advanced',
            'tags': 'anxiety,cognitive,reframing'
        },
        
        # Relationships
        {
            'category': 'relationships',
            'prompt': 'Describe a meaningful conversation you had recently. What made it meaningful?',
            'difficulty': 'beginner',
            'tags': 'relationships,connection,communication'
        },
        {
            'category': 'relationships',
            'prompt': 'Who in your life makes you feel most supported? How can you show them appreciation?',
            'difficulty': 'beginner',
            'tags': 'relationships,support,gratitude'
        },
        {
            'category': 'relationships',
            'prompt': 'What boundaries do you need to set in your relationships? Why are they important?',
            'difficulty': 'intermediate',
            'tags': 'relationships,boundaries,self-care'
        },
        {
            'category': 'relationships',
            'prompt': 'Reflect on a conflict you had recently. What could you have done differently to communicate better?',
            'difficulty': 'advanced',
            'tags': 'relationships,conflict,growth'
        },
        
        # Self-compassion
        {
            'category': 'self-compassion',
            'prompt': 'What would you say to comfort yourself during a difficult moment? Practice writing those words.',
            'difficulty': 'beginner',
            'tags': 'self-compassion,kindness,support'
        },
        {
            'category': 'self-compassion',
            'prompt': 'What are you proud of yourself for, even if no one else noticed?',
            'difficulty': 'beginner',
            'tags': 'self-compassion,pride,accomplishment'
        },
        {
            'category': 'self-compassion',
            'prompt': 'How do you treat yourself when you make a mistake? Is it how you would treat a good friend?',
            'difficulty': 'intermediate',
            'tags': 'self-compassion,mistakes,growth'
        }
    ]
    
    for prompt_data in prompts:
        prompt = JournalingPrompt(**prompt_data)
        db.session.add(prompt)
    
    db.session.commit()
    print(f"Seeded {len(prompts)} journaling prompts!")


if __name__ == '__main__':
    create_exercise_tables()
