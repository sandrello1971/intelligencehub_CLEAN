import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const GoogleAuthSuccess: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    console.log('GoogleAuthSuccess component loaded');
    
    const token = searchParams.get('token');
    const userName = searchParams.get('user');

    console.log('Token:', token ? 'Present' : 'Missing');
    console.log('User:', userName);

    if (token) {
      try {
        // Salva il token direttamente
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify({
          username: userName || 'Google User',
          first_name: userName || 'Google User'
        }));
        
        console.log('Token and user saved to localStorage');
        
        // Redirect semplice senza API call per ora
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1000);
        
      } catch (error) {
        console.error('Error in GoogleAuthSuccess:', error);
        navigate('/login');
      }
    } else {
      console.log('No token, redirecting to login');
      navigate('/login');
    }
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold">Autenticazione Google in corso...</h2>
        <p className="text-gray-600">Salvataggio credenziali...</p>
      </div>
    </div>
  );
};

export default GoogleAuthSuccess;
