import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthLayout } from "@/layouts/AuthLayout";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { GoogleSignInButton } from "@/components/ui/GoogleSignInButton";
import { PasswordStrength } from "@/components/ui/PasswordStrength";
import { useAuth } from "@/hooks/useAuth";
import { friendlyErrorMessage } from "@/lib/errors";

const MIN_PASSWORD_LENGTH = 8;
const EMAIL_PATTERN = /^\S+@\S+\.\S+$/;

type FieldErrors = Partial<
  Record<"fullName" | "email" | "password" | "confirmPassword", string>
>;

export function Signup() {
  const navigate = useNavigate();
  const { register, loginWithGoogle } = useAuth();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    // Own validation instead of the browser's default bubbles, so the
    // messages match the rest of the UI.
    const errors: FieldErrors = {};
    if (!fullName.trim()) errors.fullName = "Enter your full name.";
    if (!email.trim()) errors.email = "Enter your email.";
    else if (!EMAIL_PATTERN.test(email.trim())) errors.email = "Enter a valid email address.";
    if (password.length < MIN_PASSWORD_LENGTH) {
      errors.password = `Use at least ${MIN_PASSWORD_LENGTH} characters.`;
    }
    if (!confirmPassword) errors.confirmPassword = "Confirm your password.";
    else if (password !== confirmPassword) errors.confirmPassword = "Passwords don't match.";
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setLoading(true);
    try {
      await register({ full_name: fullName, email, password });
      navigate("/dashboard");
    } catch (err) {
      setError(friendlyErrorMessage(err));
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
      title="Create your account"
      subtitle="Free to start — no credit card required."
      footer={
        <>
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-accent hover:underline">
            Log in
          </Link>
        </>
      }
    >
        <GoogleSignInButton onCredential={handleGoogle} onError={setError} />

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <Input
          label="Full name"
          autoComplete="name"
          required
          value={fullName}
          error={fieldErrors.fullName}
          onChange={(e) => {
            setFullName(e.target.value);
            setFieldErrors((f) => ({ ...f, fullName: undefined }));
          }}
        />
        <Input
          type="email"
          label="Email"
          autoComplete="email"
          required
          value={email}
          error={fieldErrors.email}
          onChange={(e) => {
            setEmail(e.target.value);
            setFieldErrors((f) => ({ ...f, email: undefined }));
          }}
        />
        <Input
          type="password"
          label="Password"
          autoComplete="new-password"
          required
          value={password}
          error={fieldErrors.password}
          onChange={(e) => {
            setPassword(e.target.value);
            setFieldErrors((f) => ({ ...f, password: undefined }));
          }}
        />
        <PasswordStrength password={password} />
        <Input
          type="password"
          label="Confirm password"
          autoComplete="new-password"
          required
          value={confirmPassword}
          onChange={(e) => {
            setConfirmPassword(e.target.value);
            setFieldErrors((f) => ({ ...f, confirmPassword: undefined }));
          }}
          error={
            fieldErrors.confirmPassword ??
            (confirmPassword && password !== confirmPassword
              ? "Passwords don't match."
              : undefined)
          }
        />

        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}

        <Button type="submit" loading={loading} className="w-full">
          Create account
        </Button>
      </form>
    </AuthLayout>
  );
}
