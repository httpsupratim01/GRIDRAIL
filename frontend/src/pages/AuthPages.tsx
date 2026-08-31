import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { djangoApi } from "../services/api";

export function LoginPage({ admin = false }: { admin?: boolean }) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      await login(identifier, password);
      navigate(admin ? "/admin" : "/dashboard");
    } catch {
      setError("Invalid login. Check your username/email and password.");
    }
  }

  return (
    <section className="auth-panel">
      <h1>{admin ? "Admin Login" : "Passenger Login"}</h1>
      <form onSubmit={submit}>
        <input type="text" value={identifier} onChange={(e) => setIdentifier(e.target.value)} placeholder="Username or email" />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        {error && <p className="error">{error}</p>}
        <button className="primary-action">Login</button>
      </form>
      <Link to="/forgot-password">Forgot password</Link>
    </section>
  );
}

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", phone: "", password: "" });
  async function submit(event: FormEvent) {
    event.preventDefault();
    await register(form);
    navigate("/dashboard");
  }
  return (
    <section className="auth-panel">
      <h1>Create Passenger Account</h1>
      <form onSubmit={submit}>
        {Object.entries(form).map(([key, value]) => (
          <input
            key={key}
            type={key === "password" ? "password" : key === "email" ? "email" : "text"}
            value={value}
            placeholder={key.replace("_", " ")}
            onChange={(e) => setForm({ ...form, [key]: e.target.value })}
          />
        ))}
        <button className="primary-action">Register</button>
      </form>
    </section>
  );
}

export function ForgotPasswordPage() {
  return <SimplePage title="Forgot Password" body="Enter your registered email in production to receive a secure reset link. This academic build keeps the flow as a protected UI state." />;
}

export function ChangePasswordPage() {
  const { user } = useAuth();
  const [form, setForm] = useState({ current_password: "", new_password: "", confirm_password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);
    try {
      await djangoApi.post("/auth/change-password", form);
      setForm({ current_password: "", new_password: "", confirm_password: "" });
      setSuccess("Password changed successfully. Use the new password next time you login.");
    } catch (err: any) {
      const data = err.response?.data;
      setError(data?.current_password?.[0] || data?.new_password?.[0] || data?.confirm_password?.[0] || data?.non_field_errors?.[0] || "Password could not be changed.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="auth-panel password-panel">
      <span className="eyebrow">{user?.role === "ADMIN" ? "Admin Security" : "Passenger Security"}</span>
      <h1>Change Password</h1>
      <form onSubmit={submit}>
        <label>Current Password<input type="password" value={form.current_password} onChange={(e) => setForm({ ...form, current_password: e.target.value })} /></label>
        <label>New Password<input type="password" value={form.new_password} onChange={(e) => setForm({ ...form, new_password: e.target.value })} /></label>
        <label>Confirm New Password<input type="password" value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} /></label>
        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}
        <button className="primary-action" disabled={saving}>{saving ? "Changing..." : "Change Password"}</button>
      </form>
    </section>
  );
}

export function SimplePage({ title, body }: { title: string; body: string }) {
  return (
    <section className="page-card">
      <h1>{title}</h1>
      <p>{body}</p>
    </section>
  );
}
