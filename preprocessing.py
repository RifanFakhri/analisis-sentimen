"""
Text Preprocessing module for Indonesian text.
Handles: case folding, cleaning, tokenization, stopword removal, stemming.
"""

import re
import string
import nltk
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# Download NLTK data (only needed once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

# Initialize Sastrawi stemmer and stopword remover
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

stopword_factory = StopWordRemoverFactory()
# Exclude negation words from stopword list to preserve sentiment
NEGATION_WORDS = {'tidak', 'kurang', 'bukan', 'jangan', 'tak', 'tiada', 'belum'}
stopwords_id = set(stopword_factory.get_stop_words()) - NEGATION_WORDS

# Additional custom stopwords for sentiment analysis (excluding negations)
CUSTOM_STOPWORDS = {
    'yg', 'dgn', 'nya', 'utk', 'klo', 'gak', 'ga', 'gk',
    'tp', 'tpi', 'udh', 'udah', 'sdh', 'blm', 'blum',
    'bgt', 'banget', 'aja', 'sih', 'deh', 'dong', 'nih',
    'lho', 'lah', 'kan', 'ya', 'yaa', 'ko', 'kok'
}

# Normalization dictionary for informal Indonesian
NORMALIZATION_DICT = {
    'gak': 'tidak', 'ga': 'tidak', 'gk': 'tidak', 'tdk': 'tidak',
    'nggak': 'tidak', 'ngga': 'tidak', 'enggak': 'tidak',
    'yg': 'yang', 'dgn': 'dengan', 'utk': 'untuk', 'kpd': 'kepada',
    'dr': 'dari', 'pd': 'pada', 'dlm': 'dalam', 'krn': 'karena',
    'trs': 'terus', 'tp': 'tapi', 'tpi': 'tapi', 'sdh': 'sudah',
    'udh': 'sudah', 'udah': 'sudah', 'blm': 'belum', 'blum': 'belum',
    'bgt': 'sangat', 'bngt': 'sangat', 'bngtt': 'sangat',
    'sm': 'sama', 'org': 'orang', 'bkn': 'bukan',
    'klo': 'kalau', 'kl': 'kalau', 'klu': 'kalau',
    'jg': 'juga', 'jgn': 'jangan', 'lg': 'lagi',
    'emg': 'memang', 'emang': 'memang',
    'bs': 'bisa', 'aj': 'saja', 'aja': 'saja',
    'bgs': 'bagus', 'bgus': 'bagus',
    'jlk': 'jelek', 'jlek': 'jelek',
    'krg': 'kurang', 'brg': 'barang',
    'mantap': 'bagus', 'mantab': 'bagus', 'mantul': 'bagus',
    'oke': 'baik', 'ok': 'baik',
    'thx': 'terima kasih', 'tq': 'terima kasih', 'makasih': 'terima kasih',
    'mksh': 'terima kasih', 'makasi': 'terima kasih',
}


def case_folding(text):
    """Convert text to lowercase."""
    return text.lower()


def clean_text(text):
    """Remove URLs, mentions, hashtags, numbers, punctuation, and extra whitespace."""
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove mentions
    text = re.sub(r'@\w+', '', text)
    # Remove hashtags
    text = re.sub(r'#\w+', '', text)
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_text(text):
    """Normalize informal Indonesian words to standard forms."""
    words = text.split()
    normalized = [NORMALIZATION_DICT.get(word, word) for word in words]
    return ' '.join(normalized)


def tokenize(text):
    """Tokenize text into words."""
    return nltk.word_tokenize(text)


def remove_stopwords(tokens):
    """Remove Indonesian stopwords from token list."""
    all_stopwords = stopwords_id | CUSTOM_STOPWORDS
    return [token for token in tokens if token not in all_stopwords and len(token) > 1]


def stem_tokens(tokens):
    """Apply Sastrawi stemmer to each token."""
    return [stemmer.stem(token) for token in tokens]


def preprocess_text(text):
    """
    Full preprocessing pipeline:
    1. Case folding
    2. Text cleaning
    3. Normalization
    4. Tokenization
    5. Stopword removal
    6. Stemming
    """
    text = case_folding(text)
    text = clean_text(text)
    text = normalize_text(text)
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = stem_tokens(tokens)
    return ' '.join(tokens)


def preprocess_for_display(text):
    """
    Preprocessing pipeline that returns intermediate steps for display.
    Returns a dictionary with each step's result.
    """
    steps = {}

    # Step 1: Case Folding
    text_lower = case_folding(text)
    steps['case_folding'] = text_lower

    # Step 2: Cleaning
    text_clean = clean_text(text_lower)
    steps['cleaning'] = text_clean

    # Step 3: Normalization
    text_norm = normalize_text(text_clean)
    steps['normalization'] = text_norm

    # Step 4: Tokenization
    tokens = tokenize(text_norm)
    steps['tokenization'] = tokens

    # Step 5: Stopword Removal
    tokens_filtered = remove_stopwords(tokens)
    steps['stopword_removal'] = tokens_filtered

    # Step 6: Stemming
    tokens_stemmed = stem_tokens(tokens_filtered)
    steps['stemming'] = tokens_stemmed

    # Final result
    steps['final'] = ' '.join(tokens_stemmed)

    return steps
