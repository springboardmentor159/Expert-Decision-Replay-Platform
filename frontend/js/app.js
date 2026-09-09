// Application Entrypoint
import { auth } from './auth.js';
import { router } from './router.js';

async function bootstrap() {
  try {
    // Attempt session recovery
    await auth.initAuth();
  } catch (err) {
    console.warn('Session initialization:', err);
  } finally {
    // Listen for auth state changes to update routes
    auth.onChange(() => {
      router.handleRoute();
    });

    // Initial route handling
    router.handleRoute();
  }
}

// Start application once DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}
