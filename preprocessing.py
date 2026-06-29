"""
Text Preprocessing module for Indonesian text.
Handles: case folding, cleaning, tokenization, stopword removal, stemming.
"""

import re
import string
import nltk
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Download NLTK data (only needed once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Initialize Sastrawi stemmer and stopword remover
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

stopword_factory = StopWordRemoverFactory()
# Exclude negation words from stopword list to preserve sentiment
NEGATION_WORDS = {'tidak', 'kurang', 'bukan', 'jangan', 'tak', 'tiada', 'belum', 'nggak', 'gak'}
stopwords_id = set(stopword_factory.get_stop_words()) - NEGATION_WORDS

# Additional custom stopwords for sentiment analysis (excluding negations)
CUSTOM_STOPWORDS = {
    'yg', 'dgn', 'nya', 'utk', 'tp', 'tpi', 'udh', 'udah', 'sdh',
    'blm', 'blum', 'bgt', 'banget', 'aja', 'sih', 'deh', 'dong', 'nih',
    'lho', 'lah', 'kan', 'ya', 'yaa', 'ko', 'kok',
    'wkwk', 'haha', 'hahaha', 'iya', 'masih', 'lagi', 'kami', 'saya', 'aku', 'kamu'
}

# Normalization dictionary for informal Indonesian
NORMALIZATION_DICT = {
    'gak': 'tidak', 'ga': 'tidak', 'gk': 'tidak', 'tdk': 'tidak',
    'nggak': 'tidak', 'ngga': 'tidak', 'enggak': 'tidak', 'gakn': 'tidak',
    'yg': 'yang', 'dgn': 'dengan', 'utk': 'untuk', 'kpd': 'kepada',
    'dr': 'dari', 'pd': 'pada', 'dlm': 'dalam', 'krn': 'karena',
    'trs': 'terus', 'tp': 'tapi', 'tpi': 'tapi', 'sdh': 'sudah',
    'udh': 'sudah', 'udah': 'sudah', 'blm': 'belum', 'blum': 'belum',
    'bgt': 'sangat', 'bngt': 'sangat', 'bngtt': 'sangat',
    'sm': 'sama', 'org': 'orang', 'bkn': 'bukan',
    'klo': 'kalau', 'kl': 'kalau', 'klu': 'kalau', 'kpn': 'kapan',
    'krn': 'karena', 'kmrn': 'kemarin', 'skrg': 'sekarang', 'skg': 'sekarang',
    'sblm': 'sebelum', 'sblum': 'sebelum', 'jg': 'juga', 'jgn': 'jangan',
    'lg': 'lagi', 'emg': 'memang', 'emang': 'memang',
    'bs': 'bisa', 'aj': 'saja', 'aja': 'saja',
    'bgs': 'bagus', 'bgus': 'bagus', 'jlk': 'jelek', 'jlek': 'jelek',
    'krg': 'kurang', 'brg': 'barang',
    'mantap': 'bagus', 'mantab': 'bagus', 'mantul': 'bagus',
    'oke': 'baik', 'ok': 'baik', 'okeh': 'baik',
    'thx': 'terima kasih', 'tq': 'terima kasih', 'makasih': 'terima kasih',
    'mksh': 'terima kasih', 'makasi': 'terima kasih',
    'keren': 'bagus', 'lumayan': 'cukup', 'gpp': 'tidak apa apa'
}

EMOJI_PATTERN = re.compile(
    '[\U0001F600-\U0001F64F'
    '\U0001F300-\U0001F5FF'
    '\U0001F680-\U0001F6FF'
    '\U0001F1E0-\U0001F1FF'
    '\U00002702-\U000027B0'
    '\U000024C2-\U0001F251]+'
    , flags=re.UNICODE)

REPEAT_CHAR_PATTERN = re.compile(r'(\w)\1{2,}', flags=re.UNICODE)


def case_folding(text):
    """Convert text to lowercase."""
    return text.lower()


def remove_emojis(text):
    """Remove emoji and symbol characters from text."""
    return EMOJI_PATTERN.sub('', text)


def normalize_repeated_characters(text, max_repeat=2):
    """Reduce elongated characters like 'bagusss' to 'baguss'."""
    return REPEAT_CHAR_PATTERN.sub(lambda m: m.group(1) * max_repeat, text)


def clean_text(text):
    """Remove URLs, mentions, hashtags, HTML, punctuation, and extra whitespace."""
    text = text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    text = text.replace('&amp;', ' dan ').replace('&nbsp;', ' ')
    text = remove_emojis(text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = normalize_repeated_characters(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_token(word):
    """Normalize a token using the slang dictionary and repeated character reduction."""
    if word in NORMALIZATION_DICT:
        return NORMALIZATION_DICT[word]

    collapsed = re.sub(r'(\w)\1{2,}', r'\1\1', word)
    if collapsed in NORMALIZATION_DICT:
        return NORMALIZATION_DICT[collapsed]

    collapsed_single = re.sub(r'(\w)\1+', r'\1', word)
    if collapsed_single in NORMALIZATION_DICT:
        return NORMALIZATION_DICT[collapsed_single]

    return word


def normalize_text(text):
    """Normalize informal Indonesian words to standard forms."""
    words = text.split()
    normalized = [normalize_token(word) for word in words]
    normalized = [word for word in normalized if word]
    return ' '.join(normalized)


def tokenize(text):
    """Tokenize text into words."""
    try:
        return nltk.word_tokenize(text)
    except Exception as e:
        # Fallback to regex word boundary tokenization if NLTK punkt is missing/not writable
        return re.findall(r'\b\w+\b', text)


def remove_stopwords(tokens):
    """Remove Indonesian stopwords from token list while preserving negations."""
    all_stopwords = stopwords_id | CUSTOM_STOPWORDS
    return [token for token in tokens if token not in all_stopwords and len(token) > 1]


# Global stemming cache to speed up Sastrawi stemming
STEM_CACHE = {}
import time

def stem_tokens(tokens):
    """Apply Sastrawi stemmer to all tokens efficiently using batch sentence stemming and cache."""
    # Get unique uncached tokens to maintain order and uniqueness
    uncached_tokens = []
    seen = set()
    for t in tokens:
        if t not in STEM_CACHE and t not in seen:
            uncached_tokens.append(t)
            seen.add(t)
            
    if uncached_tokens:
        # Stem all uncached tokens at once
        uncached_str = " ".join(uncached_tokens)
        stemmed_str = stemmer.stem(uncached_str)
        stemmed_list = stemmed_str.split()
        
        # If count matches, populate cache
        if len(uncached_tokens) == len(stemmed_list):
            for orig, stemmed in zip(uncached_tokens, stemmed_list):
                STEM_CACHE[orig] = stemmed
        else:
            # Fallback to word-by-word stemming if count mismatches
            for token in uncached_tokens:
                STEM_CACHE[token] = stemmer.stem(token)
                
    # Return from cache
    return [STEM_CACHE[token] for token in tokens]


def preprocess_text(text):
    """
    Full preprocessing pipeline:
    1. NULL/NaN value handling
    2. Case folding
    3. Text cleaning
    4. Normalization
    5. Tokenization
    6. Stopword removal
    7. Stemming
    
    Returns empty string for NULL/NaN inputs to prevent crashes.
    """
    # NULL/NaN handling: prevent AttributeError on None or NaN values
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    
    # Convert to string in case input is not string type
    text = str(text).strip()
    if not text:  # Empty string check
        return ""
    
    start = time.perf_counter()
    try:
        text_folded = case_folding(text)
        text_cleaned = clean_text(text_folded)
        text_norm = normalize_text(text_cleaned)
        tokens = tokenize(text_norm)
        tokens = remove_stopwords(tokens)
        tokens = stem_tokens(tokens)
        result = ' '.join(tokens)
        print(f"Preprocess selesai dalam {time.perf_counter()-start:.3f} detik")
        return result
    except Exception as e:
        # Log error but return empty string instead of crashing
        print(f"Warning: Error preprocessing text '{text[:50]}...': {str(e)}")
        return ""


def preprocess_for_display(text):
    """
    Preprocessing pipeline that returns intermediate steps for display.
    Returns a dictionary with each step's result.
    Includes NULL/NaN value handling for robustness.
    """
    steps = {}
    
    # NULL/NaN handling
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return {
            'case_folding': '[NULL/EMPTY]',
            'cleaning': '[NULL/EMPTY]',
            'normalization': '[NULL/EMPTY]',
            'tokenization': [],
            'stopword_removal': [],
            'stemming': [],
            'final': '',
            'error': 'Input is NULL or NaN'
        }
    
    # Convert to string in case input is not string type
    text = str(text).strip()
    if not text:
        return {
            'case_folding': '',
            'cleaning': '',
            'normalization': '',
            'tokenization': [],
            'stopword_removal': [],
            'stemming': [],
            'final': '',
            'error': 'Input is empty string'
        }
    
    try:
        text_lower = case_folding(text)
        steps['case_folding'] = text_lower

        text_clean = clean_text(text_lower)
        steps['cleaning'] = text_clean

        text_norm = normalize_text(text_clean)
        steps['normalization'] = text_norm

        tokens = tokenize(text_norm)
        steps['tokenization'] = tokens

        tokens_filtered = remove_stopwords(tokens)
        steps['stopword_removal'] = tokens_filtered

        tokens_stemmed = stem_tokens(tokens_filtered)
        steps['stemming'] = tokens_stemmed

        steps['final'] = ' '.join(tokens_stemmed)
    except Exception as e:
        steps['error'] = f"Preprocessing error: {str(e)}"
        steps['final'] = ''

    return steps
