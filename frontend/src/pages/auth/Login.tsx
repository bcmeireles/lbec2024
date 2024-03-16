import React, { useState } from 'react';
import waves from '../../wickedbackground.svg';

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
          localStorage.setItem('token', data.token);
          window.location.href = '/dashboard';
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
    <div className="h-screen bg-white flex items-center justify-center px-6 relative">
      <img src={waves} alt="Waves" className="absolute bottom-0 left-0 w-full h-full" />
      <div className="z-10 relative">
      <div className="w-full max-w-sm">
        <form onSubmit={handleFormSubmit} className="bg-white rounded px-8 pt-6 pb-8 mb-4 bg-opacity-80">
          <div className="mb-4">
            <label htmlFor="email" className="block text-gray-700 text-sm font-bold mb-2">Email:</label>
            <input type="email" name="email" value={form.email} onChange={handleInputChange} className=" appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
          </div>
          <div className="mb-6">
            <label htmlFor="password" className="block text-gray-700 text-sm font-bold mb-2">Password:</label>
            <input type="password" name="password" value={form.password} onChange={handleInputChange} className=" appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
          </div>
          {error && <p className="text-red-500 text-xs italic">{error}</p>}
          <div className="flex items-center justify-between">
            <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full">Login</button>
          </div>
        </form>
      </div>
      </div>
    </div>
  );
};

export default Login;
