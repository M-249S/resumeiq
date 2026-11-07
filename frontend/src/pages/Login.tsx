import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { GoogleSignInButton } from "@/components/ui/GoogleSignInButton";
import { useAuth } from "@/hooks/useAuth";
import { friendlyErrorMessage, isServerSideFailure } from "@/lib/errors";

const EMAIL_PATTERN = /^\S+@\S+\.\S+$/;

export function Login() {
  const navigate = useNavigate();
  const { login, loginWithGoogle } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    // Own validation instead of the browser's default bubbles, so the
    // messages match the rest of the UI.
    const nextEmailError = !email.trim()
      ? "Enter your email."
      : !EMAIL_PATTERN.test(email.trim())
        ? "Enter a valid email address."
        : "";
    const nextPasswordError = password ? "" : "Enter your password.";
    setEmailError(nextEmailError);
    setPasswordError(nextPasswordError);
    if (nextEmailError || nextPasswordError) return;

    setLoading(true);

    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      // Deliberately generic for credential failures: don't reveal whether
      // the email exists. Server/network problems get their own message so
      // a sleeping backend isn't mistaken for a wrong password.
      setError(
        isServerSideFailure(err)
          ? friendlyErrorMessage(err)
          : "Incorrect email or password.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogle(credential: string) {
    setError("");
    try {
      await loginWithGoogle(credential);
      navigate("/dashboard");
    } catch (err) {
      setError(friendlyErrorMessage(err, "Google sign-in failed. Please try again."));
    }
  }

  return (
    <AuthLayout
      title="Log in"
      subtitle="Welcome back — pick up where you left off."
      footer={
        <>
          Don't have an account?{" "}
          <Link to="/signup" className="font-medium text-accent hover:underline">
            Sign up
          </Link>
        </>
      }
    >
        <GoogleSignInButton onCredential={handleGoogle} onError={setError} />

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <Input
          type="email"
          label="Email"
          autoComplete="email"
          required
          value={email}
          error={emailError || undefined}
          onChange={(e) => {
            setEmail(e.target.value);
            setEmailError("");
          }}
        />
        <Input
          type="password"
          label="Password"
          autoComplete="current-password"
          required
          value={password}
          error={passwordError || undefined}
          onChange={(e) => {
            setPassword(e.target.value);
            setPasswordError("");
          }}
        />

        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}

        <Button type="submit" loading={loading} className="w-full">
          Log in
        </Button>
      </form>
    </AuthLayout>
  );
}
