"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

interface SearchResult {
  document_id: string;
  document_title: string;
  document_filename: string;
  document_type: string;
  chunk_id: string;
  chunk_text: string;
  chunk_index: number;
  similarity_score: number;
}

export default function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError("Please enter a search query");
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    setLoading(true);
    setError("");
    setSearched(false);

    try {
      const response = await fetch("http://localhost:8001/api/v1/search/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          query,
          limit: 10,
          similarity_threshold: 0.3,
        }),
      });

      if (response.status === 401) {
        router.push("/login");
        return;
      }

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Search failed");
      }

      const data = await response.json();
      setResults(data.results);
      setSearched(true);
    } catch (err: any) {
      setError(err.message || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Semantic Search</h1>
          <div className="flex gap-4">
            <button
              onClick={() => router.push("/documents")}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
            >
              My Documents
            </button>
            <button
              onClick={() => router.push("/")}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
            >
              Home
            </button>
          </div>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <form onSubmit={handleSearch} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search your documents
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-md text-lg"
                  placeholder="e.g., contract terms, payment obligations, legal definitions..."
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="px-8 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {loading ? "Searching..." : "Search"}
                </button>
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Search uses AI to find semantically similar content in your documents
              </p>
            </div>
          </form>
        </div>

        {/* Results */}
        {searched && (
          <div className="bg-white rounded-lg shadow-md">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold">
                Results ({results.length})
              </h2>
              {results.length > 0 && (
                <p className="text-sm text-gray-600 mt-1">
                  Showing most relevant matches for &quot;{query}&quot;
                </p>
              )}
            </div>

            {results.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <p className="text-lg mb-2">No results found</p>
                <p className="text-sm">
                  Try different keywords or check if you have uploaded documents
                </p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {results.map((result, idx) => (
                  <div key={result.chunk_id} className="p-6 hover:bg-gray-50">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                            {Math.round(result.similarity_score * 100)}% match
                          </span>
                          <span className="text-xs text-gray-500">
                            {result.document_type.toUpperCase()}
                          </span>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900">
                          {result.document_title}
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">
                          {result.document_filename} • Chunk {result.chunk_index + 1}
                        </p>
                      </div>
                    </div>
                    <div className="mt-3 p-4 bg-gray-50 rounded border border-gray-200">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {result.chunk_text}
                      </p>
                    </div>
                    <div className="mt-2">
                      <a
                        href={`/documents`}
                        className="text-sm text-blue-600 hover:text-blue-700"
                      >
                        View full document →
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {!searched && !loading && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center text-gray-500">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <p className="text-lg">Enter a search query to get started</p>
            <p className="text-sm mt-2">
              Our AI will find relevant content across all your documents
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
