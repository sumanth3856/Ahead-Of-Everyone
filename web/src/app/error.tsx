'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Global Application Error Caught:", error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glass rounded-2xl p-8 max-w-md w-full text-center">
        <h2 className="text-xl font-bold text-red-400 mb-4">Something went wrong!</h2>
        <p className="text-sm text-muted mb-6">
          Check the browser console for exact error details.
        </p>
        <button
          onClick={
            // Attempt to recover by trying to re-render the segment
            () => reset()
          }
          className="bg-brand/10 border border-brand/50 text-brand font-semibold tracking-widest text-xs uppercase py-2 px-4 rounded hover:bg-brand/90 hover:text-white transition-all duration-300"
        >
          Try again
        </button>
      </div>
    </div>
  )
}
