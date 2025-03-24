import requests
from bs4 import BeautifulSoup
import validators
from collections import Counter
import re

class SEOAnalyzer:
    def __init__(self, url):
        if not validators.url(url):
            raise ValueError("Invalid URL. Please enter a valid URL starting with 'http://' or 'https://'")
        self.url = url
        self.soup = self.get_page_content()

    def get_page_content(self):
        """Fetch page content and parse with BeautifulSoup"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'lxml')
        else:
            raise Exception(f"Error fetching the URL: {response.status_code}")

    def get_meta_tags(self):
        """Extract meta title, description, and keywords"""
        meta_data = {
            "title": str(self.soup.title.string) if self.soup.title else "No title tag found",
            "description": "",
            "keywords": ""
        }
        description_tag = self.soup.find("meta", attrs={"name": "description"})
        keywords_tag = self.soup.find("meta", attrs={"name": "keywords"})

        if description_tag:
            meta_data["description"] = description_tag.get("content", "No description available")
        if keywords_tag:
            meta_data["keywords"] = keywords_tag.get("content", "No keywords available")

        return meta_data

    def get_header_tags(self):
        """Extract header tags (H1, H2, etc.)"""
        headers = {}
        for i in range(1, 7):
            headers[f"h{i}"] = [tag.text.strip() for tag in self.soup.find_all(f"h{i}")]
        return headers

    def get_image_alt_tags(self):
        """Check for images and their alt attributes"""
        images = self.soup.find_all("img")
        image_data = []
        for img in images:
            alt_text = img.get("alt", "No alt text")
            src = img.get("src", "No source")
            image_data.append({"src": src, "alt": alt_text})
        return image_data

    def calculate_word_count(self):
        """Calculate total word count on the page"""
        texts = self.soup.stripped_strings
        word_count = sum(len(text.split()) for text in texts)
        return word_count
    
    def get_keyword_density(self):
        """Calculate keyword density on the page"""
        texts = self.soup.get_text()
        words = re.findall(r'\b\w+\b', texts.lower())  # Extract words and convert to lowercase
        total_words = len(words)
        word_counts = Counter(words)

        keyword_density = {word: (count / total_words) * 100 for word, count in word_counts.items() if count > 1}
        return dict(sorted(keyword_density.items(), key=lambda x: x[1], reverse=True)[:10])  # Top 10 keywords

    def analyze(self):
        """Run all analysis functions and return the results"""
        return {
            "meta_tags": self.get_meta_tags(),
            "headers": self.get_header_tags(),
            "image_alt_tags": self.get_image_alt_tags(),
            "word_count": self.calculate_word_count(),
            "keyword_density": self.get_keyword_density(),
        }

if __name__ == "__main__":
    url = input("Enter a website URL: ")
    try:
        analyzer = SEOAnalyzer(url)
        results = analyzer.analyze()
        print("\nSEO Analysis Results:")
        for key, value in results.items():
            print(f"\n{key.upper()}: ")
            print(value)
    except Exception as e:
        print(f"Error: {e}")
