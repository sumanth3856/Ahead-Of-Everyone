import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

const supabase = createClient(supabaseUrl, supabaseKey)

async function testAuth() {
  console.log("Signing up test user...")
  const { data, error } = await supabase.auth.signUp({
    email: 'newtest2@aheadofeveryone.com',
    password: 'password123',
    options: {
      data: {
        full_name: 'Test Agent'
      }
    }
  })
  
  if (error) {
    console.error("Signup error:", error.message)
  } else {
    console.log("Signup success:", data.user?.id)
  }

  console.log("Logging in test user...")
  const { data: loginData, error: loginError } = await supabase.auth.signInWithPassword({
    email: 'newtest2@aheadofeveryone.com',
    password: 'password123',
  })

  if (loginError) {
    console.error("Login error:", loginError.message)
  } else {
    console.log("Login success:", loginData.user?.id)
  }
}

testAuth()
