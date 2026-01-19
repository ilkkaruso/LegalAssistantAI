export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Legal Assistant AI</h1>
        <p className="text-xl text-muted-foreground">
          AI-powered legal document assistant
        </p>
        <div className="mt-8 flex gap-4 justify-center">
          <a
            href="/login"
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            Sign In
          </a>
          <a
            href="/register"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition"
          >
            Get Started
          </a>
        </div>
        <div className="mt-4 flex gap-4 justify-center text-sm">
          <a
            href="/documents"
            className="text-blue-600 hover:text-blue-700 underline"
          >
            View My Documents
          </a>
          <span className="text-gray-400">|</span>
          <a
            href="/search"
            className="text-blue-600 hover:text-blue-700 underline"
          >
            Search Documents
          </a>
        </div>
      </div>
    </main>
  )
}
