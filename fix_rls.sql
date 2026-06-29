-- Drop any existing select policy
DROP POLICY IF EXISTS "Users can view their own digests" ON public.digests_cache;
DROP POLICY IF EXISTS "Public digests are viewable by everyone" ON public.digests_cache;
DROP POLICY IF EXISTS "Users can view their own or global digests" ON public.digests_cache;

-- Enable RLS just in case
ALTER TABLE public.digests_cache ENABLE ROW LEVEL SECURITY;

-- Create correct policy
CREATE POLICY "Users can view their own or global digests" 
ON public.digests_cache 
FOR SELECT 
USING (
  auth.uid() = user_id OR user_id IS NULL
);
