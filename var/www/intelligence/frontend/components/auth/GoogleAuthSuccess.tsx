import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const GoogleAuthSuccess: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { refreshAuth } = useAuth();

  useEffect(() => {
    const token = searchParams.get('token');
    const userName = searchParams.get('user');

    if (token) {
      // Salva il token direttamente
      localStorage.setItem('token', token);
      
      // Imposta l'header di autorizzazione per axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Ottieni i dati utente dal backend usando il token
      fetchUserData(token);
    } else {
      // Se non c'è token, torna al login
      navigate('/login');
    }
  }, [searchParams, navigate, refreshAuth]);

  const fetchUserData = async (token: string) => {
    try {
      // Chiama l'endpoint del profilo utente per ottenere i dati completi
      const response = await axios.get('/api/v1/auth/profile');
      const userData = response.data;
      
      // Salva i dati utente
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Refresh dell'AuthContext per aggiornare lo stato
      await refreshAuth();
      
      // Ora naviga alla dashboard
      navigate('/admin');
      
    } catch (error) {
      console.error('Error fetching user data:', error);
      // Se fallisce, torna al login
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold">Autenticazione Google in corso...</h2>
        <p className="text-gray-600">Verifica credenziali...</p>
      </div>
    </div>
  );
};

export default GoogleAuthSuccess;
