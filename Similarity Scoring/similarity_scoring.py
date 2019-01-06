from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import justext
from html_similarity import similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from db_handler import DatabaseHandler
from urls_pairing import fill_url_pairs


def get_cosine_sim(*strs):
    # Calculate cosine distance from sklearn
    vectors = [t for t in get_vectors(*strs)]
    return cosine_similarity(vectors)[0, 1]


def get_vectors(*strs):
    # Get term frequency using sklearn CountVectorizer
    text = [t for t in strs]
    vectorizer = CountVectorizer(text)
    vectorizer.fit(text)
    return vectorizer.transform(text).toarray()


def get_tf_sim(docs):
    # Get cosine distance of tfidf vectors
    tfidf = TfidfVectorizer().fit_transform(docs)
    pairwise_similarity = tfidf * tfidf.T
    return pairwise_similarity[0, 1]


def get_jaccard_sim(str1, str2):
    # Calculate jaccard similarity
    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))


def remover_boiler_code(decoded_full_html):
    # Get content of page, remove html code
    extracted_content = ''
    paragraphs = justext.justext(decoded_full_html, justext.get_stoplist("English"))

    extracted_content = "\n".join([paragraph.text.lower() for paragraph in paragraphs])

    return extracted_content


def main():
    db_handler = DatabaseHandler()
    # 1. find all referer urls, save them in referer table for ease of processing
    db_handler.find_distinct()
    # 2. add content_text column to the pages table
    db_handler.add_column()
    # 3. use the boiler removal function to get the content text
    db_handler.update_content_text(remover_boiler_code)
    # 4. construct the url pairs
    fill_url_pairs(db_handler)
    # 5. update the similarity scores with structural and semantic similarity functions
    db_handler.update_sim_score(similarity, get_cosine_sim, )


if __name__ == '__main__':
    main()
