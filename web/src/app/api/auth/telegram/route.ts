import { NextResponse } from 'next/server'
import crypto from 'crypto'
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

// Helper to verify Telegram data
function verifyTelegramHash(data: any, botToken: string): boolean {
  const secretKey = crypto.createHash('sha256').update(botToken).digest()
  
  // Create the data check string
  const checkString = Object.keys(data)
    .filter(key => key !== 'hash')
    .sort()
    .map(key => `${key}=${data[key]}`)
    .join('\n')

  const hmac = crypto.createHmac('sha256', secretKey).update(checkString).digest('hex')
  return hmac === data.hash
}

// Deterministic shadow password generator
function generateShadowPassword(telegramId: string, botToken: string): string {
  return crypto.createHmac('sha256', botToken).update(`shadow_${telegramId}`).digest('hex') + "Aa1!" // ensure complexity requirements
}

export async function GET(request: Request) {
  try {
    const { searchParams, origin } = new URL(request.url)
    
    // Extract Telegram data from query params
    const telegramData: any = {}
    searchParams.forEach((value, key) => {
      telegramData[key] = value
    })

    // 1. Verify the payload hash
    const botToken = process.env.TELEGRAM_BOT_TOKEN
    if (!botToken) {
      console.error("Missing TELEGRAM_BOT_TOKEN env variable")
      return NextResponse.redirect(`${origin}/login?message=Server configuration error`)
    }

    if (!telegramData.hash || !verifyTelegramHash(telegramData, botToken)) {
      console.error("Invalid Telegram hash")
      return NextResponse.redirect(`${origin}/login?message=Invalid authentication payload`)
    }

    // Check auth date to prevent replay attacks (e.g. older than 24 hours)
    const authDate = parseInt(telegramData.auth_date, 10)
    const now = Math.floor(Date.now() / 1000)
    if (now - authDate > 86400) {
      return NextResponse.redirect(`${origin}/login?message=Authentication expired`)
    }

    const telegramId = telegramData.id
    const email = `${telegramId}@telegram.local`
    const password = generateShadowPassword(telegramId, botToken)
    const fullName = telegramData.first_name + (telegramData.last_name ? ` ${telegramData.last_name}` : '')

    // 2. Initialize Supabase Admin Client (to bypass RLS for user creation)
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
    const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
    
    if (!serviceRoleKey) {
      console.error("Missing SUPABASE_SERVICE_ROLE_KEY")
      return NextResponse.redirect(`${origin}/login?message=Server configuration error`)
    }

    // Use the admin client to find or create the user
    const adminSupabase = createServerClient(supabaseUrl, serviceRoleKey, {
      cookies: {
        getAll() { return [] },
        setAll() {}
      }
    })

    // Try to sign in first to see if the user exists
    let userExists = true
    
    // 3. Create user if they don't exist
    // We use the admin client to explicitly create the user, bypassing rate limits and allowing auto-confirm
    const { data: adminData, error: adminError } = await adminSupabase.auth.admin.createUser({
      email: email,
      password: password,
      email_confirm: true,
      user_metadata: {
        name: fullName,
        provider_id: telegramId
      }
    })

    // If the error is 'User already registered', it's fine.
    if (adminError && adminError.message !== 'User already registered') {
       console.error("Admin user creation error:", adminError)
       // If it fails for another reason, we might still be able to sign in if they already existed
       // but we will log it.
    }

    // 4. Issue the actual session using the SSR client so cookies are set!
    const cookieStore = await cookies()
    const ssrSupabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll()
          },
          setAll(cookiesToSet) {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          },
        },
      }
    )

    const { error: signInError } = await ssrSupabase.auth.signInWithPassword({
      email,
      password
    })

    if (signInError) {
      console.error("Sign in error:", signInError)
      return NextResponse.redirect(`${origin}/login?message=Failed to establish secure session`)
    }

    // 5. Success! Redirect to dashboard settings where they initiated the link
    return NextResponse.redirect(`${origin}/dashboard/settings`)
  } catch (error) {
    console.error("Unexpected error during Telegram auth:", error)
    // Return a generic fallback error page redirect without exposing stack traces
    const origin = new URL(request.url).origin
    return NextResponse.redirect(`${origin}/login?message=An unexpected error occurred`)
  }
}
