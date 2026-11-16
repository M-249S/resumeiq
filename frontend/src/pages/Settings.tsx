import { startTransition, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/landing/Navbar";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/useToast";
import { deleteAccount } from "@/services/auth";
import { friendlyErrorMessage } from "@/lib/errors";

export function Settings() {
  const { user, logout } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const [confirming, setConfirming] = useState(false);
  const [typed, setTyped] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");

  const email = user?.email ?? "";
  // Same rule as the server: case and surrounding spaces don't matter.
  const matches = typed.trim().toLowerCase() === email.toLowerCase();

  function cancel() {
    setConfirming(false);
    setTyped("");
    setError("");
  }

  async function handleDelete(event: FormEvent) {
    event.preventDefault();
    if (!matches || deleting) return;

    setDeleting(true);
    setError("");
    try {
      await deleteAccount(typed.trim());
      // Leave and log out in one transition: logging out alone while still
      // on this protected route would bounce the user to /login instead of
      // the home page.
      startTransition(() => {
        navigate("/", { replace: true });
        logout();
      });
      toast.show("Your account and data were deleted.", "success");
    } catch (err) {
      setError(friendlyErrorMessage(err));
      setDeleting(false);
    }
  }

  return (
    <div className="min-h-screen bg-paper">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="font-display text-2xl font-medium text-ink">Settings</h1>
        <p className="mt-1 text-ink-muted">Manage your account and your data.</p>

        <Card className="mt-8 p-6">
          <h2 className="font-medium text-ink">Account</h2>
          <dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-ink-faint">Name</dt>
              <dd className="mt-0.5 text-ink">{user?.full_name}</dd>
            </div>
            <div>
              <dt className="text-ink-faint">Email</dt>
              <dd className="mt-0.5 break-all text-ink">{email}</dd>
            </div>
          </dl>
        </Card>

        <Card className="mt-6 border-danger/40 p-6">
          <h2 className="font-medium text-danger">Delete account</h2>
          <p className="mt-2 text-sm text-ink-muted">
            This permanently deletes your account and every resume analysis you
            have saved. It takes effect immediately and cannot be undone.
          </p>

          {!confirming ? (
            <Button
              variant="secondary"
              className="mt-5 border-danger/50 text-danger hover:border-danger"
              onClick={() => setConfirming(true)}
            >
              Delete my account
            </Button>
          ) : (
            <form onSubmit={handleDelete} className="mt-5 max-w-md space-y-4" noValidate>
              <Input
                label={`Type ${email} to confirm`}
                type="email"
                autoComplete="off"
                autoFocus
                value={typed}
                onChange={(event) => setTyped(event.target.value)}
                error={error}
              />
              <div className="flex gap-3">
                <Button
                  type="submit"
                  className="bg-danger text-paper hover:bg-danger/90"
                  disabled={!matches}
                  loading={deleting}
                >
                  Permanently delete
                </Button>
                <Button type="button" variant="ghost" onClick={cancel} disabled={deleting}>
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </Card>
      </main>
    </div>
  );
}
