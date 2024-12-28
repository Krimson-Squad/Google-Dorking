from collections import Counter
import re

class SearchEngine:
    def __init__(self):
        self.base_url = "https://www.google.com/search"
        self.stop_words = set([
            "the", "is", "in", "and", "of", "to", "a", "it", "that", "on", "for", "with", "as", "at", "this", "by", "an", "be", "are", "was", "or", "from", "but", "not", "they", "have", "has", "had", "will", "would", "can", "could", "should", "do", "does", "did"
        ])
        
    def get_search_results(self, query, num_pages=3):
        """Fetch search results from Google based on user input, loop through multiple pages."""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        results = []
        
        for page in range(num_pages):
            params = {
                'q': query,
                'hl': 'en',  
                'start': page * 10  
            }

            response = requests.get(self.base_url, headers=headers, params=params)
            if response.status_code == 200:
                page_results = self.parse_results(response.text)
                results.extend(page_results)
                time.sleep(1)  
            else:
                print(f"{Fore.RED}Failed to fetch results for page {page + 1}. Status Code: {response.status_code}")
        
        return results

    def parse_results(self, html_content):
        """Parse the HTML content to extract search results."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []

        for item in soup.select('div.tF2Cxc'):
            title = item.select_one('h3').text if item.select_one('h3') else None
            link = item.select_one('a')['href'] if item.select_one('a') else None
            snippet = item.select_one('div.VwiC3b').text if item.select_one('div.VwiC3b') else None
            
            if title and link:
                results.append({'title': title, 'link': link, 'snippet': snippet})

        return results

    def categorize_results(self, query):
        """Categorize search results into Identity Reveal and Related Documents."""
        categories = {
            "Identity Reveal": ['site:linkedin.com', 'site:github.com', 'site:facebook.com', 'site:instagram.com', 'site:twitter.com', 'site:wikipedia.org'],
            "Related Documents": ['filetype:pdf', 'filetype:docx', 'filetype:xlsx']
        }
        
        categorized_results = {key: [] for key in categories}
        
        for category, dorks in categories.items():
            for dork in dorks:
                dork_query = f'{query} {dork}'
                results = self.get_search_results(dork_query, num_pages=1)
                categorized_results[category].extend(results)
        
        return categorized_results

    def display_categorized_results(self, categorized_results):
        """Display the categorized results in card frames."""
        print(Fore.YELLOW + pyfiglet.figlet_format("Search Results"))
        
        for category, results in categorized_results.items():
            print(Fore.CYAN + f"\n{category}:")
            if not results:
                print(Fore.RED + "No results found.")
            else:
                for result in results:
                    print(Fore.MAGENTA + "+" + "-" * 78 + "+")
                    print(Fore.MAGENTA + "| " + Fore.BLUE + f"Title: {result['title']}".ljust(77) + Fore.MAGENTA + "|")
                    print(Fore.MAGENTA + "| " + Fore.GREEN + f"Link: {result['link']}".ljust(77) + Fore.MAGENTA + "|")
                    snippet = result['snippet'] or "No snippet available."
                    snippet_lines = [snippet[i:i+75] for i in range(0, len(snippet), 75)]
                    for line in snippet_lines:
                        print(Fore.MAGENTA + "| " + Fore.YELLOW + line.ljust(77) + Fore.MAGENTA + "|")
                    print(Fore.MAGENTA + "+" + "-" * 78 + "+")

    def extract_keywords(self, categorized_results):
        """Extract and count common keywords from categorized results."""
        all_text = ""

     
        for category, results in categorized_results.items():
            for result in results:
                all_text += (result['title'] or "") + " "
                all_text += (result['snippet'] or "") + " "
        
     
        words = re.findall(r'\b\w+\b', all_text.lower())
        filtered_words = [word for word in words if word not in self.stop_words]
        
        
        word_counts = Counter(filtered_words)
        return word_counts.most_common(10) 



if __name__ == "__main__":
    print(Fore.MAGENTA + pyfiglet.figlet_format("Google Dorking"))
    query = input(Fore.YELLOW + "Enter your search query: ")
    search_engine = SearchEngine()
    try:
        categorized_results = search_engine.categorize_results(query)
        search_engine.display_categorized_results(categorized_results)

       
        print(Fore.YELLOW + "\nExtracting common keywords...")
        common_keywords = search_engine.extract_keywords(categorized_results)
        print(Fore.GREEN + "Top Keywords:")
        for keyword, count in common_keywords:
            print(Fore.CYAN + f"{keyword}: {count}")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")
