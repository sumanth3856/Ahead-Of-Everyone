'use server'

import { createClient } from '@/utils/supabase/server'
import { revalidatePath } from 'next/cache'
import { cookies } from 'next/headers'
import crypto from 'crypto'

const HMAC_SECRET = process.env.SUPABASE_SERVICE_ROLE_KEY || 'default_fallback_secret_only_for_dev'
const COOKIE_NAME = 'email_otp_session'

function signData(data: object): string {
  const payload = Buffer.from(JSON.stringify(data)).toString('base64')
  const signature = crypto.createHmac('sha256', HMAC_SECRET).update(payload).digest('base64')
  return `${payload}.${signature}`
}

function verifyData(token: string): any | null {
  try {
    const [payload, signature] = token.split('.')
    const expectedSignature = crypto.createHmac('sha256', HMAC_SECRET).update(payload).digest('base64')
    if (signature !== expectedSignature) return null
    return JSON.parse(Buffer.from(payload, 'base64').toString('utf-8'))
  } catch (e) {
    return null
  }
}

export async function updateProfile(formData: FormData) {
  try {
    const supabase = await createClient()
    const { data: { user }, error: authError } = await supabase.auth.getUser()

    if (authError || !user) return { error: 'Not authenticated' }

    const fullName = formData.get('full_name') as string

    let profileUpdate: any = { full_name: fullName, updated_at: new Date().toISOString() };
    const { error: profileError } = await supabase.from('profiles').update(profileUpdate).eq('id', user.id)

    if (profileError) return { error: 'Failed to update profile' }

    const { error: userError } = await supabase.auth.updateUser({ data: { full_name: fullName } })
    if (userError) return { error: 'Failed to update user details' }

    revalidatePath('/dashboard', 'layout')
    return { success: true }
  } catch (error) {
    return { error: 'An unexpected error occurred' }
  }
}

export async function requestEmailUpdate(newEmail: string) {
  try {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return { error: 'Not authenticated' }
    if (user.email === newEmail) return { error: 'New email is identical to current email.' }

    // Check if user has linked Telegram
    const { data: profile } = await supabase.from('profiles').select('telegram_chat_id').eq('id', user.id).single()
    if (!profile?.telegram_chat_id) {
      return { error: 'You must link your Telegram account before changing your email address.' }
    }

    // Generate 6-digit OTP
    const otp = Math.floor(100000 + Math.random() * 900000).toString()

    // Send OTP to Telegram directly via Telegram API
    const botToken = process.env.TELEGRAM_BOT_TOKEN
    if (!botToken) return { error: 'Telegram Bot Token not configured on server.' }

    const cookieStore = await cookies()
    const existingSessionToken = cookieStore.get(COOKIE_NAME)?.value
    if (existingSessionToken) {
      const existingSession = verifyData(existingSessionToken)
      if (existingSession?.messageId && existingSession?.chatId) {
        await fetch(`https://api.telegram.org/bot${botToken}/deleteMessage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id: existingSession.chatId,
            message_id: existingSession.messageId
          })
        }).catch(() => {})
      }
    }
    
    const message = `Security Alert 🚨\n\nA request to change your Daily Tech Digest email to ${newEmail} was initiated.\n\nYour Verification Code is: *${otp}*\n\nThis code expires in 5 minutes.`
    
    const tgResponse = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: profile.telegram_chat_id,
        text: message,
        parse_mode: 'Markdown'
      })
    })

    if (!tgResponse.ok) {
      return { error: 'Failed to deliver OTP via Telegram.' }
    }

    const tgData = await tgResponse.json()

    // Create session cookie data
    const sessionData = {
      otp,
      newEmail,
      userId: user.id,
      expiresAt: Date.now() + 5 * 60 * 1000, // 5 minutes
      messageId: tgData.result?.message_id,
      chatId: profile.telegram_chat_id
    }

    // Set secure HttpOnly cookie
    cookieStore.set(COOKIE_NAME, signData(sessionData), {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 5 * 60 // 5 minutes
    })

    return { requireOtp: true }
  } catch (error: any) {
    return { error: error.message || 'An unexpected error occurred' }
  }
}

export async function confirmEmailUpdate(otp: string) {
  try {
    const cookieStore = await cookies()
    const sessionToken = cookieStore.get(COOKIE_NAME)?.value

    if (!sessionToken) return { error: 'OTP session expired or missing.' }

    const sessionData = verifyData(sessionToken)
    if (!sessionData) return { error: 'Invalid or tampered OTP session.' }

    const botToken = process.env.TELEGRAM_BOT_TOKEN

    if (Date.now() > sessionData.expiresAt) {
      if (sessionData.messageId && sessionData.chatId && botToken) {
        await fetch(`https://api.telegram.org/bot${botToken}/deleteMessage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chat_id: sessionData.chatId, message_id: sessionData.messageId })
        }).catch(() => {})
      }
      cookieStore.delete(COOKIE_NAME)
      return { error: 'OTP expired. Please request a new one.' }
    }

    if (sessionData.otp !== otp) {
      return { error: 'Incorrect verification code.' }
    }

    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()
    if (!user || user.id !== sessionData.userId) return { error: 'User mismatch.' }

    // Execute email update
    const { error: updateError } = await supabase.auth.updateUser({ email: sessionData.newEmail })
    
    if (updateError) {
      return { error: updateError.message || 'Failed to update email in identity provider.' }
    }

    // Delete OTP message and send success message
    if (sessionData.messageId && sessionData.chatId && botToken) {
      await fetch(`https://api.telegram.org/bot${botToken}/deleteMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: sessionData.chatId, message_id: sessionData.messageId })
      }).catch(() => {})

      await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: sessionData.chatId,
          text: `✅ *Success*\n\nYour Daily Tech Digest email address has been securely updated to:\n\`${sessionData.newEmail}\``,
          parse_mode: 'Markdown'
        })
      }).catch(() => {})
    }

    // Clear session on success
    cookieStore.delete(COOKIE_NAME)
    revalidatePath('/dashboard', 'layout')
    
    return { success: true, message: 'Email address securely updated.' }
  } catch (error: any) {
    return { error: error.message || 'An unexpected error occurred' }
  }
}
