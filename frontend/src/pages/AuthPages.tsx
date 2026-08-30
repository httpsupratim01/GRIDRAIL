import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

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
  return <SimplePage title="Change Password" body="Password changes are handled by the authenticated Django account workflow and can be connected to the profile endpoint." />;
}

export function SimplePage({ title, body }: { title: string; body: string }) {
  return (
    <section className="page-card">
      <h1>{title}</h1>
      <p>{body}</p>
    </section>
  );
}
