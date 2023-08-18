from supabase import create_client, Client

url:str = 'https://nyuvdcewxadfcquchcgy.supabase.co'
key:str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55dXZkY2V3eGFkZmNxdWNoY2d5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTAwODM4MjksImV4cCI6MjAwNTY1OTgyOX0.rktn1-34hqAruUjLCdn2AlAfgLb-7RVsLGL-VtuVdbk'
supabase: Client = create_client(url, key)