'use client'

import { useEffect, useRef } from 'react'

export default function TelegramLoginWidget({ botName, authUrl }: { botName: string, authUrl: string }) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return
    
    // Clear any existing script to prevent duplicates on strict mode
    containerRef.current.innerHTML = ''

    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.setAttribute('data-telegram-login', botName)
    script.setAttribute('data-size', 'large')
    script.setAttribute('data-radius', '8')
    script.setAttribute('data-auth-url', authUrl)
    script.setAttribute('data-request-access', 'write')
    script.async = true

    containerRef.current.appendChild(script)
  }, [botName, authUrl])

  return (
    <div 
      ref={containerRef} 
      className="flex justify-center w-full min-h-[40px]"
    >
      {/* The Telegram script injects the iframe here */}
    </div>
  )
}
