import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from ai.nlp_engine import NLPEngine
import json

nlp = NLPEngine()

# Test cases in different Indian languages
test_cases = [
    ('en', 'Help me drowning need rescue please flood'),
    ('hi', 'बचाओ मदद चाहिए बाढ़ में फँस गए हैं'),
    ('ml', 'രക്ഷിക്കാൻ സഹായം വേണം'),
    ('ta', 'மீட்க த தேவை'),
    ('bn', 'সাহায্য প্রয়োজন'),
]

results = []

for lang, msg in test_cases:
    result = nlp.classify_sos(msg)
    results.append({
        'input_lang': lang,
        'input': msg,
        'detected': result['language_detected'],
        'confidence': result['language_confidence'],
        'has_survivor': result['has_survivor_signal'],
        'count': result['survivor_count_estimate'],
        'location': result['location_extracted'],
        'priority': result['priority_score'],
        'level': result['priority_level'],
    })

with open('test_nlp_output.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(results, ensure_ascii=False, indent=2))
print("Results written to test_nlp_output.json")