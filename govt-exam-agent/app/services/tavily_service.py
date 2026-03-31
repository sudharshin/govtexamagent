from tavily import TavilyClient
from typing import List, Dict


class TavilyService:
    def __init__(self):
        # 🔐 Move this to ENV in real projects
        self.client = TavilyClient(api_key="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")

    # ==========================================
    # 🔍 SEARCH EXAM CONTENT (DEDUP + FILTER)
    # ==========================================
    def search_exam_content(self, exam_name: str) -> Dict:
        exam_name = exam_name.lower().strip()

        queries = [
            f"{exam_name} previous year question paper pdf",
            f"{exam_name} solved papers pdf download",
            f"{exam_name} question paper with answers pdf"
        ]

        all_results: List[Dict] = []
        seen_links = set()

        for query in queries:
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5
                )

                for result in response.get("results", []):
                    url = result.get("url", "").strip()
                    title = result.get("title", "").strip().lower()

                    if not url:
                        continue

                    normalized_url = self._normalize_url(url)

                    # ============================
                    # ✅ REMOVE DUPLICATES
                    # ============================
                    if normalized_url in seen_links:
                        continue

                    # ============================
                    # ✅ FILTER IRRELEVANT RESULTS
                    # ============================
                    if exam_name not in title and exam_name not in normalized_url:
                        continue

                    if not any(k in normalized_url for k in ["pdf", "question", "paper", "exam"]):
                        continue

                    seen_links.add(normalized_url)

                    all_results.append({
                        "title": result.get("title"),
                        "url": url
                    })

            except Exception as e:
                print(f"[Tavily Search Error] {e}")
                continue

        return {"results": all_results}

    # ==========================================
    # 📄 EXTRACT CONTENT FROM URL
    # ==========================================
    def extract_from_url(self, url: str) -> Dict:
        try:
            response = self.client.extract(urls=[url])

            if not response.get("results"):
                return {"results": []}

            cleaned_results = []

            for res in response.get("results", []):
                content = res.get("content") or res.get("raw_content")

                if not content or len(content.strip()) < 50:
                    continue

                cleaned_results.append({
                    "url": url,
                    "content": content
                })

            return {"results": cleaned_results}

        except Exception as e:
            print(f"[Tavily Extract Error] {e}")
            return {"results": []}

    # ==========================================
    # 🔗 NORMALIZE URL (IMPORTANT 🔥)
    # ==========================================
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URLs to avoid duplicates:
        - remove trailing slashes
        - remove query params
        - lowercase
        """
        try:
            url = url.lower().strip()

            # Remove query params
            if "?" in url:
                url = url.split("?")[0]

            # Remove trailing slash
            if url.endswith("/"):
                url = url[:-1]

            return url

        except:
            return url