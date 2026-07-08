const fs = require('fs');
const { createClient } = require('@supabase/supabase-js');
const env = fs.readFileSync('.env.local', 'utf8').split('\n').reduce((acc, line) => {
  const [key, val] = line.split('=');
  if (key && val) acc[key.trim()] = val.trim();
  return acc;
}, {});

const supabase = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);

async function check() {
  const { data: digests, error } = await supabase.from('digests_cache').select('topic, generated_date_ist, created_at, user_id');
  console.log('Total digests:', digests.length);
  const userIds = new Set(digests.map(d => d.user_id));
  const topics = new Set(digests.map(d => d.topic));
  console.log('Unique users:', userIds);
  console.log('Unique topics:', topics);
}
check();
