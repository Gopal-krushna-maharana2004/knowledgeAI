import requests
from bs4 import BeautifulSoup

def scrape_topic_summary(topic):
    """
    Scrapes a summary for the given topic from Wikipedia.
    """
    if not topic:
        return "No topic provided."
    
    # Format topic for Wikipedia URL
    search_url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
    
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code != 200:
            # Try title case
            search_url = f"https://en.wikipedia.org/wiki/{topic.title().replace(' ', '_')}"
            response = requests.get(search_url, timeout=10)
            
        if response.status_code != 200:
            return f"Could not find information for '{topic}' on Wikipedia."
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get the first few paragraphs
        paragraphs = soup.find_all('p')
        summary = ""
        count = 0
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 50:
                summary += text + "\n\n"
                count += 1
            if count >= 3: # Limit to 3 paragraphs
                break
        
        if not summary:
            return f"Information for '{topic}' found, but could not extract a summary."
            
        return summary
    except Exception as e:
        return f"An error occurred while scraping: {str(e)}"

def validate_answer_with_web(question, user_answer, expected_answer):
    """
    Attempts to validate the user's answer by searching for evidence on Wikipedia.
    """
    def clean(s):
        import re
        return re.sub(r'[^\w\s]', '', s.lower()).strip()

    user_clean = clean(user_answer)
    expected_clean = clean(expected_answer)
    
    # 1. If user answer is exactly/nearly expected answer after cleaning
    if user_clean in expected_clean or expected_clean in user_clean:
        return True, "Correct! Match found in database."
        
    # Handle common plural/singular or fragment matches
    if len(user_clean) > 3 and (user_clean[:4] in expected_clean or expected_clean[:4] in user_clean):
        return True, "Correct! (Partial or plural match)"

    # Use the expected answer or key parts of the question to search
    query = expected_answer if len(expected_answer) > 3 else f"{question} {expected_answer}"
    search_url = f"https://en.wikipedia.org/wiki/Special:Search?search={query.replace(' ', '+')}"
    
    try:
        response = requests.get(search_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check if we were redirected to a specific page or staying on search results
        page_text = soup.get_text().lower()
        
        # 2. Check if user's answer appears in the scraped content in context of the topic
        if user_clean in page_text and len(user_clean) > 3:
            return True, f"Correct! I found evidence for '{user_answer}' in my research."
            
        return False, f"I couldn't find strong evidence for '{user_answer}'. The expected answer was '{expected_answer}'."
        
    except Exception:
        # Fallback to simple matching if scraping fails
        if user_clean in expected_clean or expected_clean in user_clean:
            return True, "Correct (fallback validation)."
        return False, f"Validation failed. Expected: {expected_answer}"

if __name__ == "__main__":
    # Test
    print(scrape_topic_summary("Quantum Mechanics"))
    print(validate_answer_with_web("What is the powerhouse of the cell?", "Mitochondrion", "mitochondria"))
