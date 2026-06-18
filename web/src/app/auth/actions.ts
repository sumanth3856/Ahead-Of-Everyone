'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { createClient } from '@/utils/supabase/server'

export async function login(formData: FormData) {
  let errorMsg = null;
  try {
    const email = formData.get('email') as string
    const password = formData.get('password') as string
    const supabase = await createClient()

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) {
      errorMsg = error.message;
    }
  } catch (error: any) {
    console.error("Login action crashed:", error);
    errorMsg = "An unexpected server error occurred.";
  }

  if (errorMsg) {
    return redirect(`/login?message=${encodeURIComponent(errorMsg)}`)
  }

  revalidatePath('/', 'layout')
  return redirect('/dashboard')
}

export async function signup(formData: FormData) {
  let errorMsg = null;
  try {
    const email = formData.get('email') as string
    const password = formData.get('password') as string
    const name = formData.get('name') as string
    const supabase = await createClient()

    // 1. Sign up the user
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: name,
        }
      }
    })

    if (authError) {
      errorMsg = authError.message;
    } else {
      // 2. We use the service role key to insert the profile directly
      if (authData.user && process.env.SUPABASE_SERVICE_ROLE_KEY) {
        const { createClient: createSupabaseClient } = await import('@supabase/supabase-js');
        const supabaseAdmin = createSupabaseClient(
          process.env.NEXT_PUBLIC_SUPABASE_URL!,
          process.env.SUPABASE_SERVICE_ROLE_KEY
        );

        const { error: profileError } = await supabaseAdmin
          .from('profiles')
          .insert({
            id: authData.user.id,
            full_name: name,
          });
          
        if (profileError) {
          console.warn("Could not create profile record:", profileError.message);
        }
      } else if (authData.user && !process.env.SUPABASE_SERVICE_ROLE_KEY) {
        console.warn("SUPABASE_SERVICE_ROLE_KEY is missing. Skipping profile creation.");
      }
    }
  } catch (error: any) {
    console.error("Signup action crashed:", error);
    errorMsg = "An unexpected server error occurred.";
  }

  if (errorMsg) {
    return redirect(`/signup?message=${encodeURIComponent(errorMsg)}`)
  }

  revalidatePath('/', 'layout')
  return redirect('/dashboard')
}


export async function loginWithTelegram() {
  const supabase = await createClient()

  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'custom:telegram',
    options: {
      redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
      queryParams: {
        bot_id: process.env.NEXT_PUBLIC_TELEGRAM_BOT_ID as string,
      }
    },
  })

  if (error) {
    console.error("Telegram OAuth error:", error.message)
    redirect(`/login?message=${encodeURIComponent(error.message)}`)
  }

  if (data.url) {
    redirect(data.url)
  }
}

export async function logout() {
  const supabase = await createClient()

  const { error } = await supabase.auth.signOut()

  if (error) {
    console.error("Logout error:", error.message)
    redirect(`/login?message=${encodeURIComponent(error.message)}`)
  }

  revalidatePath('/', 'layout')
  redirect('/login')
}
