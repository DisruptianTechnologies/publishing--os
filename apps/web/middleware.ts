import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isPublic = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
]);

export default clerkMiddleware(async (auth, req) => {
  const isDemo = process.env.NEXT_PUBLIC_DEMO_MODE === 'true' || process.env.DEMO_MODE === 'true';
  if (!isPublic(req) && !isDemo) {
    await auth.protect();
  }
});

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)', '/(api|trpc)(.*)']
};
