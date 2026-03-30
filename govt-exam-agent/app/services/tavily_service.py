from tavily import TavilyClient

class TavilyService:
    def __init__(self):
        self.client = TavilyClient(api_key="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")

    def search_exam_content(self, exam_name: str):
        exam_name = exam_name.lower().strip()

        # 🔥 Generic smart queries
        queries = [
            f"{exam_name} previous year question paper pdf",
            f"{exam_name} exam solved papers pdf download",
            f"{exam_name} question paper with answers pdf"
        ]

        all_results = []

        for query in queries:
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5
                )

                for result in response.get("results", []):
                    url = result.get("url", "").lower()
                    title = result.get("title", "").lower()

                    # 🔥 FILTER (important)
                    # Keep only relevant results
                    if exam_name not in title and exam_name not in url:
                        continue

                    # Optional: keep only useful sources
                    if not any(k in url for k in ["pdf", "question", "paper", "exam"]):
                        continue

                    all_results.append(result)

            except Exception as e:
                print(f"Error: {e}")
                continue

        return {"results": all_results}

    def extract_from_url(self, url: str):
        try:
            return self.client.extract(urls=[url])
        except Exception as e:
            return {"error": str(e)}