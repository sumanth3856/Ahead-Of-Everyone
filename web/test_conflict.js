const fs = require('fs');
const { createClient } = require('@supabase/supabase-js');
const env = fs.readFileSync('.env.local', 'utf8').split('\n').reduce((acc, line) => {
  const [key, val] = line.split('=');
  if (key && val) acc[key.trim()] = val.trim();
  return acc;
}, {});

const supabase = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);

async function check() {
  const { data, error } = await supabase.from('digests_cache').upsert({
    topic: 'v4:test_conflict',
    file_id: '123',
    generated_date_ist: '2026-07-08',
    user_id: null
  }, { onConflict: 'topic' });
  console.log('Error:', error);
}
check();
