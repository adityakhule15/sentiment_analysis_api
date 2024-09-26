import pandas as pd
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import groq  

# Set up Groq client with your API key
client = groq.Client(api_key='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')

# Function to extract reviews from the uploaded file
def extract_reviews(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        raise ValueError('Invalid file format')
    
    # Assuming the reviews are in a column named 'Review'
    if 'Review' not in df.columns:
        raise ValueError('No review column found in the file')
    
    return df['Review'].tolist()

# Function to analyze sentiment using Groq LLM
def analyze_sentiment(review_text):
    prompt = f"Analyze the sentiment of the following review: {review_text}. Is it positive, neutral, or negative?"

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    
    sentiment = chat_completion.choices[0].message.content.strip().lower()
    
    sentiment_scores = {
        'positive': 0,
        'negative': 0,
        'neutral': 0
    }
    
    if "positive" in sentiment:
        sentiment_scores['positive'] = 1
        # print('positive')
    elif "negative" in sentiment:
        sentiment_scores['negative'] = 1
        # print('negative')
    elif "neutral" in sentiment:
        sentiment_scores['neutral'] = 1
        # print('neutral')
    else:
        # Return an error or log the unexpected result
        print(f"Unexpected sentiment response: {sentiment}")
    
    return sentiment_scores


# Main function to handle uploaded file and process reviews
def process_reviews(file):
    reviews = extract_reviews(file)
    sentiment_scores = defaultdict(float)
    
    for review in reviews:
        sentiment = analyze_sentiment(review)
        sentiment_scores['positive'] += sentiment.get('positive', 0)
        sentiment_scores['negative'] += sentiment.get('negative', 0)
        sentiment_scores['neutral'] += sentiment.get('neutral', 0)
    
    total_reviews = len(reviews)
    
    if total_reviews == 0:
        raise ValueError("No reviews found in the file")
    
    # Average out the sentiment scores
    return {key: score / total_reviews for key, score in sentiment_scores.items()}

# View to handle the file upload and return the sentiment analysis results
@csrf_exempt
def upload_reviews(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        try:
            sentiment_results = process_reviews(file)
            return JsonResponse(sentiment_results, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
