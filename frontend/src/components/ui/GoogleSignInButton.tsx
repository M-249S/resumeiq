import { useEffect, useRef } from "react";

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;
const GSI_SRC = "https://accounts.google.com/gsi/client";

interface GoogleIdApi {
  initialize: (config: {
    client_id: string;
    callback: (response: { credential: string }) => void;
  }) => void;
  renderButton: (
    parent: HTMLElement,
    options: Record<string, string | number>,
  ) => void;
}

declare global {
  interface Window {
    google?: { accounts: { id: GoogleIdApi } };
  }
}

let scriptPromise: Promise<void> | null = null;

function loadGoogleScript(): Promise<void> {
  if (window.google?.accounts?.id) return Promise.resolve();
  if (!scriptPromise) {
    scriptPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = GSI_SRC;
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => {
        scriptPromise = null;
        reject(new Error("Failed to load Google sign-in."));
      };
      document.head.appendChild(script);
    });
  }
  return scriptPromise;
}

interface Props {
  onCredential: (credential: string) => void;
  onError: (message: string) => void;
}

/**
 * Renders Google's official "Sign in with Google" button. Renders nothing when
 * VITE_GOOGLE_CLIENT_ID is not set, so the app works without Google configured.
 */
export function GoogleSignInButton({ onCredential, onError }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  // Keep the latest handlers without re-initialising Google's SDK on every render.
  const handlers = useRef({ onCredential, onError });
  useEffect(() => {
    handlers.current = { onCredential, onError };
  });

  useEffect(() => {
    if (!CLIENT_ID) return;
    let cancelled = false;

    loadGoogleScript()
      .then(() => {
        const container = containerRef.current;
        const google = window.google;
        if (cancelled || !container || !google) return;

        google.accounts.id.initialize({
          client_id: CLIENT_ID,
          callback: (response) => handlers.current.onCredential(response.credential),
        });
        google.accounts.id.renderButton(container, {
          type: "standard",
          theme: "outline",
          size: "large",
          text: "continue_with",
          shape: "rectangular",
          logo_alignment: "left",
          width: Math.min(Math.round(container.offsetWidth) || 320, 400),
        });
      })
      .catch(() => handlers.current.onError("Couldn't load Google sign-in. Check your connection."));

    return () => {
      cancelled = true;
    };
  }, []);

  if (!CLIENT_ID) return null;

  return (
    <>
      <div className="flex justify-center" ref={containerRef} style={{ minHeight: 44 }} />
      <div className="my-5 flex items-center gap-3 text-xs text-ink-faint" aria-hidden>
        <span className="h-px flex-1 bg-border" />
        or
        <span className="h-px flex-1 bg-border" />
      </div>
    </>
  );
}
