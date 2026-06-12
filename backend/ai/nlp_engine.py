import re
import sys
import os
from typing import Dict, Any, Tuple

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import NLP_MODE

# Comprehensive dictionary of 10 Indian languages and their distress/SOS keywords
KEYWORDS: Dict[str, list] = {
    "Hindi": ["help", "bachao", "madad", "phaanse", "doob", "paani", "sos", "bachana", "mushkil", "sankat", "fasna", "phasa"],
    "Bengali": ["sahajya", "bachao", "madad", "dube", "jal", "bipod", "sos", "banchao", "jol", "dubeche", "banya", "bonna", "eshechhe"],
    "Tamil": ["udavi", "paayungal", "apathu", "tanneer", "salavungal", "thannir", "sos", "kapathu", "velam"],
    "Telugu": ["sahayam", "bachao", "madapu", "vellu", "niru", "aapada", "sos", "kapadandi", "varada", "neeru"],
    "Marathi": ["madad", "bachava", "saklya", "paani", "aapat", "sos", "vaachva", "pani", "duble"],
    "Kannada": ["sahaya", "kappadu", "niru", "apaththu", "rakshisi", "sos", "neeru", "banya", "tapa"],
    "Malayalam": ["sahayam", "raksha", "vellam", "apakadham", "sos", "rakshikku", "pralayam", "kooduthal"],
    "Gujarati": ["madad", "bachavo", "paani", "aapat", "sankat", "sos", "pani", "bachao", "pura"],
    "Punjabi": ["madad", "bachao", "paani", "musibat", "khatra", "sos", "hadd", "pani", "bachana"],
    "Odia": ["sahaya", "bachao", "pani", "bipada", "sangkata", "sos", "banya", "pani", "raksha"]
}

# English fallback/supplement keywords
ENGLISH_SOS = ["help", "rescue", "drowning", "flood", "stuck", "trapped", "water", "sos", "emergency", "survivor", "stranded"]

# Large list of 200+ major flood-prone and high-risk districts/cities in India across flood-affected regions
INDIAN_DISTRICTS = [
    # Kerala
    "wayanad", "kodagu", "kozhikode", "malappuram", "idukki", "ernakulam", "thrissur", "palakkad", 
    "alappuzha", "kottayam", "pathanamthitta", "kollam", "thiruvananthapuram", "kasaragod", "kannur",
    # Assam
    "cachar", "dhubri", "barpeta", "nagaon", "karimganj", "morigaon", "goalpara", "dhemaji", 
    "lakhimpur", "dibrugarh", "jorhat", "sibsagar", "tinsukia", "kokrajhar", "bongaigaon", 
    "nalbari", "kamrup", "baksa", "udalguri", "sonitpur", "darrang", "charaideo", "hailakandi", 
    "biswanath", "hazaribagh", "majuli", "karbi", "dima hasao", "south salmara", "west karbi",
    # Bihar
    "muzaffarpur", "darbhanga", "sitamarhi", "khagaria", "samastipur", "madhubani", "purnia", 
    "katihar", "araria", "kishanganj", "saharsa", "supaul", "madhepura", "bhagalpur", "patna", 
    "gaya", "saran", "vaishali", "sheohar", "east champaran", "west champaran", "gopalganj", 
    "siwan", "begusarai", "munger", "khagaria", "buxar", "bhojpur", "nalanda", "rohtas",
    # West Bengal
    "howrah", "hooghly", "medinipur", "murshidabad", "jalpaiguri", "darjeeling", "cooch behar", 
    "alipurduar", "malda", "nadia", "purulia", "bankura", "birbhum", "bardhaman", "kalimpong",
    # Karnataka & Maharashtra (Western Ghats / Cellular Dead Zones)
    "udupi", "uttara kannada", "dakshina kannada", "shimoga", "chikmagalur", "kolhapur", 
    "sangli", "satara", "thane", "raigad", "ratnagiri", "sindhudurg", "pune", "nagpur", 
    "nashik", "jalgaon", "solapur", "amravati", "aurangabad", "nanded", "yavatmal",
    # Tamil Nadu
    "chennai", "cuddalore", "thoothukudi", "madurai", "tirunelveli", "kanyakumari", "kanchipuram", 
    "tiruvallur", "tanjore", "nagapattinam", "coimbatore", "salem", "trichy", "vellore",
    # Odisha
    "balangir", "kendrapara", "jagatsinghpur", "puri", "cuttack", "ganjam", "bhadrak", 
    "balasore", "jajpur", "khordha", "mayurbhanj", "koraput", "malkangiri", "rayagada", 
    "kalahandi", "sambalpur", "bargarh", "angul", "dhenkanal", "nayagarh",
    # Gujarat
    "surat", "bharuch", "vadodara", "rajkot", "amreli", "junagadh", "ahmedabad", "jamnagar", 
    "bhavnagar", "kutch", "valsad", "navsari", "anand", "kheda", "mehsana",
    # Punjab & Jammu/Kashmir
    "amritsar", "gurdaspur", "firozpur", "jalandhar", "kapurthala", "rupnagar", "ludhiana", 
    "patiala", "bathinda", "pathankot", "srinagar", "jammu", "anantnag", "baramulla", "kupwara",
    # Uttar Pradesh
    "gorakhpur", "deoria", "ballia", "varanasi", "allahabad", "prayagraj", "lucknow", "kanpur",
    "ayodhya", "barabanki", "bahraich", "shravasti", "balrampur", "basti", "siddharthnagar",
    # Major hubs & landmarks often cited in emergency texts
    "station", "market", "bridge", "hospital", "temple", "church", "mosque", "school", "highway",
    "village", "nagar", "bazar", "chowk", "road", "colony", "taluk", "panchayat", "district"
]

class NLPEngine:
    def __init__(self):
        self.mode = NLP_MODE
        self.classifier = None
        
        if self.mode == "transformer":
            try:
                # Import here to avoid bloating process memory if not using GPU/transformers
                from transformers import pipeline
                print("[AI Engine] Loading Hugging Face bert-base-multilingual-cased pipeline on GPU/CPU...")
                # Initialize pipeline for zero shot classification
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="bert-base-multilingual-cased",
                    device=0  # GPU device 0
                )
                print("[AI Engine] Transformer mode successfully initialized!")
            except Exception as e:
                print(f"[AI Engine WARNING] Failed to load Hugging Face pipeline: {e}")
                print("[AI Engine] Falling back gracefully to KEYWORD Mode (offline-resilient).")
                self.mode = "keyword"

    def detect_language_keyword(self, text: str) -> Tuple[str, float]:
        """Heuristic language detection based on keyword match frequencies"""
        text_lower = text.lower()
        matches_per_lang = {}
        total_matches = 0

        for lang, kws in KEYWORDS.items():
            matches = sum(1 for kw in kws if kw in text_lower)
            matches_per_lang[lang] = matches
            total_matches += matches

        # English keyword match helper
        eng_matches = sum(1 for kw in ENGLISH_SOS if kw in text_lower)
        matches_per_lang["English"] = eng_matches
        total_matches += eng_matches

        if total_matches == 0:
            # Check for general Indian character patterns or default
            return "English", 0.5

        # Find the language with the most keyword matches
        detected_lang = max(matches_per_lang, key=matches_per_lang.get)
        confidence = matches_per_lang[detected_lang] / total_matches
        return detected_lang, round(confidence, 2)

    def extract_survivor_estimate(self, text: str) -> int:
        """Extracts survivor counts from digits or contextual plurals"""
        text_lower = text.lower()
        
        # Regex search for digits
        digits = re.findall(r'\b\d+\b', text_lower)
        if digits:
            num = int(digits[0])
            # Clamp to reasonable survivor size from a single message (e.g. max 50)
            if 0 < num <= 50:
                return num

        # Context-based plural heuristics
        multiple_survivor_words = [
            "family", "people", "children", "kids", "log", "bacche", "bachon", "family members",
            "parivar", "hum", "we are", "trapped here", "humlog", "kutumbam", "kudumbam"
        ]
        
        if any(word in text_lower for word in multiple_survivor_words):
            return 3  # reasonable estimate for family/group size if no specific digit is given
            
        return 1  # default to at least 1 survivor

    def extract_location(self, text: str) -> str:
        """Search text for known Indian cities/districts/landmarks"""
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text_clean.split()
        
        found_locations = []
        for loc in INDIAN_DISTRICTS:
            # Multi-word location handling (e.g., "south salmara", "east champaran")
            if " " in loc:
                if loc in text_clean:
                    found_locations.append(loc)
            else:
                if loc in words:
                    found_locations.append(loc)
        
        if found_locations:
            # Return capitalized version of the first match
            return found_locations[0].title()
            
        return "Unknown Location"

    def _detect_script(self, text: str) -> str:
        """Detect the writing script to pre-filter language candidates."""
        # Bengali script range: U+0980–U+09FF
        bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
        # Gurmukhi (Punjabi) range: U+0A00–U+0A7F
        gurmukhi_chars = sum(1 for c in text if '\u0A00' <= c <= '\u0A7F')
        # Gujarati range: U+0A80–U+0AFF
        gujarati_chars = sum(1 for c in text if '\u0A80' <= c <= '\u0AFF')
        # Devanagari (Hindi/Marathi) range: U+0900–U+097F
        devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        # Malayalam range: U+0D00–U+0D7F
        malayalam_chars = sum(1 for c in text if '\u0D00' <= c <= '\u0D7F')
        # Tamil range: U+0B80–U+0BFF
        tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        # Telugu range: U+0C00–U+0C7F
        telugu_chars = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')
        # Kannada range: U+0C80–U+0CFF
        kannada_chars = sum(1 for c in text if '\u0C80' <= c <= '\u0CFF')

        script_map = {
            "Bengali": bengali_chars,
            "Punjabi": gurmukhi_chars,
            "Gujarati": gujarati_chars,
            "Hindi": devanagari_chars,
            "Marathi": devanagari_chars,
            "Malayalam": malayalam_chars,
            "Tamil": tamil_chars,
            "Telugu": telugu_chars,
            "Kannada": kannada_chars,
        }

        max_lang = max(script_map, key=script_map.get)
        if script_map[max_lang] > 2:
            return max_lang
        return "unknown"

    def classify_sos(self, raw_message: str) -> Dict[str, Any]:
        """
        Classifies incoming SOS messages. Returns dict containing language, confidence,
        survivor estimate, location hints, has_survivor_signal, and priority metrics.
        """
        if not raw_message or not raw_message.strip():
            return {
                "language_detected": "English",
                "language_confidence": 0.0,
                "has_survivor_signal": False,
                "survivor_count_estimate": 0,
                "location_extracted": "Unknown Location",
                "priority_score": 0.0,
                "priority_level": "LOW"
            }

        # 1. Script detection (most reliable for non-Latin scripts)
        script_lang = self._detect_script(raw_message)

        # 2. Keyword matching (as before)
        lang, confidence = self.detect_language_keyword(raw_message)

        # 3. If script detection found a clear winner, trust it over keywords
        if script_lang != "unknown":
            lang = script_lang
            confidence = 1.0

        # Step 2: Extract survivors count and location
        survivor_estimate = self.extract_survivor_estimate(raw_message)
        location_hint = self.extract_location(raw_message)

        has_survivor_signal = False
        priority_score = 0.0
        
        # Step 3: Run Model Prediction depending on Mode
        if self.mode == "transformer" and self.classifier:
            try:
                candidate_labels = ["distress signal", "survivor report", "normal message"]
                result = self.classifier(raw_message, candidate_labels=candidate_labels)
                
                # Sum the score of distress-related labels
                scores_dict = dict(zip(result["labels"], result["scores"]))
                distress_score = scores_dict["distress signal"] + scores_dict["survivor report"]
                
                if distress_score >= 0.45:
                    has_survivor_signal = True
                    # Scale score based on AI distress score + survivor estimates
                    priority_score = (distress_score * 70) + min(survivor_estimate * 8, 30)
                else:
                    has_survivor_signal = False
                    priority_score = distress_score * 30
                    
            except Exception as e:
                # Inline error handling: fallback silently to keyword logic on prediction crash
                print(f"[AI Engine ERROR] Transformer inference error: {e}. Falling back to keywords.")
                has_survivor_signal, priority_score = self._compute_keyword_sos_priority(raw_message, survivor_estimate)
        else:
            # Keyword mode priority score calculation
            has_survivor_signal, priority_score = self._compute_keyword_sos_priority(raw_message, survivor_estimate)

        # Clamp priority score between 0.0 and 100.0
        priority_score = min(max(priority_score, 0.0), 100.0)
        
        # Categorize priority levels
        if priority_score >= 75:
            priority_level = "CRITICAL"
        elif priority_score >= 50:
            priority_level = "HIGH"
        elif priority_score >= 25:
            priority_level = "MEDIUM"
        else:
            priority_level = "LOW"

        return {
            "language_detected": lang,
            "language_confidence": float(confidence),
            "has_survivor_signal": has_survivor_signal,
            "survivor_count_estimate": int(survivor_estimate),
            "location_extracted": location_hint,
            "priority_score": round(float(priority_score), 2),
            "priority_level": priority_level
        }

    def _compute_keyword_sos_priority(self, raw_message: str, survivor_estimate: int) -> Tuple[bool, float]:
        """Calculates SOS signal presence and priority scores based on keyword density"""
        text_lower = raw_message.lower()
        
        # Count matched keywords in text
        match_count = 0
        for lang, kws in KEYWORDS.items():
            match_count += sum(1 for kw in kws if kw in text_lower)
        match_count += sum(1 for kw in ENGLISH_SOS if kw in text_lower)

        has_survivor_signal = match_count > 0
        
        if has_survivor_signal:
            # Score matches: density + survivor multiplier
            priority_score = (match_count * 15) + min(survivor_estimate * 12, 40)
        else:
            priority_score = 0.0

        return has_survivor_signal, priority_score
