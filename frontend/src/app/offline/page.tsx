export default function OfflinePage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="mb-4 text-6xl">📡</div>
        <h1 className="mb-2 text-3xl font-bold text-gray-900">
          You're offline
        </h1>
        <p className="text-gray-600">
          Please check your internet connection and try again.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="mt-6 rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    </div>
  );
}
