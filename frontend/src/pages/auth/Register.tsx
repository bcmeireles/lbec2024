import React, { useState } from 'react';

interface IRegisterForm {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

const Register: React.FC = () => {
  const [form, setForm] = useState<IRegisterForm>({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [passwordError, setPasswordError] = useState<string | null>(null);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setForm((prevForm) => ({ ...prevForm, [name]: value }));
    setPasswordError(null);
  };

  const handleFormSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (form.password !== form.confirmPassword) {
      setPasswordError('Passwords do not match');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          password: form.password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log(data);
        // Handle successful registration (e.g. redirect to login page)
      } else {
        const errorData = await response.json();
        console.error(errorData);
        // Handle registration error (e.g. display error message)
      }
    } catch (error) {
      console.error(error);
      // Handle network error (e.g. display error message)
    }
  };

  return (
    <form onSubmit={handleFormSubmit}>
      <label htmlFor="name">Name:</label>
      <input type="text" name="name" value={form.name} onChange={handleInputChange} />

      <label htmlFor="email">Email:</label>
      <input type="email" name="email" value={form.email} onChange={handleInputChange} />

      <label htmlFor="password">Password:</label>
      <input type="password" name="password" value={form.password} onChange={handleInputChange} />

      <label htmlFor="confirmPassword">Confirm Password:</label>
      <input
        type="password"
        name="confirmPassword"
        value={form.confirmPassword}
        onChange={handleInputChange}
      />
      {passwordError && <p>{passwordError}</p>}

      <button type="submit">Register</button>
    </form>
  );
};

export default Register;
