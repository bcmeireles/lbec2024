import React, { useState } from 'react';

interface ILoginForm {
  email: string;
  password: string;
}

const Login: React.FC = () => {
  const [form, setForm] = useState<ILoginForm>({
    email: '',
    password: '',
  });

  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setForm((prevForm) => ({ ...prevForm, [name]: value }));
  };

  const handleFormSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  
    try {
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      });
  
      if (response.ok) {
        const data = await response.json();
  
        if (data.success) {
          // Handle successful login (e.g. store the JWT token in local storage and redirect to the dashboard)
          console.log("logged in");
        } else {
          setError(data.message);
        }
      } else {
        setError('An error occurred while logging in');
      }
    } catch (error) {
      console.error(error);
      setError('An error occurred while logging in');
    }
  };
  

  return (
    <form onSubmit={handleFormSubmit}>
      <label htmlFor="email">Email:</label>
      <input type="email" name="email" value={form.email} onChange={handleInputChange} />

      <label htmlFor="password">Password:</label>
      <input type="password" name="password" value={form.password} onChange={handleInputChange} />

      {error && <p>{error}</p>}

      <button type="submit">Login</button>
    </form>
  );
};

export default Login;
