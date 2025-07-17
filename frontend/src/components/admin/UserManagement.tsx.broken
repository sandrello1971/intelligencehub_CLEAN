import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, UserX, UserCheck, AlertTriangle } from 'lucide-react';
import axios from 'axios';

interface User {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface FormData {
  first_name: string;
  last_name: string;
  email: string;
  role: string;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState<FormData>({
    first_name: '',
    last_name: '',
    email: '',
    role: 'operator'
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/admin/users/');
      setUsers(response.data || []);
    } catch (error) {
      console.error('Errore caricamento utenti:', error);
    } finally {
      setLoading(false);
    }
  };
  const deleteUserPermanent = async (user: User) => {
    if (window.confirm(`⚠️  ATTENZIONE: Cancellazione DEFINITIVA di ${user.first_name} ${user.last_name}!\n\nQuesta operazione è IRREVERSIBILE e rimuoverà completamente l'utente dal database.\n\nSei assolutamente sicuro?`)) {
      if (window.confirm(`Ultima conferma: Cancellare DEFINITIVAMENTE ${user.email}?`)) {
        try {
          await axios.delete(`/api/v1/admin/users/${user.id}/permanent`);
          loadUsers();
          alert('Utente cancellato definitivamente dal database!');
        } catch (error) {
          console.error('Errore cancellazione definitiva:', error);
          alert('Errore durante la cancellazione definitiva dell\'utente');
        }
      }
    }
  };


  const createUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const userData = {
        ...formData,
        username: formData.email,
        password: 'password123',
        name: formData.first_name,
        surname: formData.last_name,
        permissions: {},
        is_active: true
      };
      
      await axios.post('/api/v1/admin/users/', userData);
      setShowCreateForm(false);
      setFormData({ first_name: '', last_name: '', email: '', role: 'operator' });
      loadUsers();
      alert('Utente creato con successo! Password: password123');
    } catch (error) {
      console.error('Errore creazione utente:', error);
      alert('Errore durante la creazione dell\'utente');
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (user: User) => {
    setEditingUser(user);
    setFormData({
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      email: user.email,
      role: user.role
    });
    setShowEditForm(true);
  };

  const updateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    
    setLoading(true);
    try {
      const userData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        role: formData.role
      };
      
      await axios.patch(`/api/v1/admin/users/${editingUser.id}`, userData);
      setShowEditForm(false);
      setEditingUser(null);
      setFormData({ first_name: '', last_name: '', email: '', role: 'operator' });
      loadUsers();
      alert('Utente aggiornato con successo!');
    } catch (error) {
      console.error('Errore aggiornamento utente:', error);
      alert('Errore durante l\'aggiornamento dell\'utente');
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (user: User) => {
    if (window.confirm(`Sei sicuro di voler ${user.is_active ? 'disattivare' : 'attivare'} ${user.first_name} ${user.last_name}?`)) {
      try {
        await axios.patch(`/api/v1/admin/users/${user.id}`, {
          is_active: !user.is_active
        });
        loadUsers();
        alert(`Utente ${user.is_active ? 'disattivato' : 'attivato'} con successo!`);
      } catch (error) {
        console.error('Errore cambio stato utente:', error);
        alert('Errore durante il cambio di stato dell\'utente');
      }
    }
  };

  const deleteUser = async (user: User) => {
    if (window.confirm(`Sei sicuro di voler disattivare definitivamente ${user.first_name} ${user.last_name}? (L'utente non verrà eliminato ma disattivato)`)) {
      try {
        await axios.delete(`/api/v1/admin/users/${user.id}`);
        loadUsers();
        alert('Utente disattivato con successo!');
      } catch (error) {
        console.error('Errore disattivazione utente:', error);
        alert('Errore durante la disattivazione dell\'utente');
      }
    }
  };

  const UserForm = ({ isEdit = false }: { isEdit?: boolean }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-xl font-bold mb-4">
          {isEdit ? 'Modifica Utente' : 'Crea Nuovo Utente'}
        </h3>
        <form onSubmit={isEdit ? updateUser : createUser} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nome
            </label>
            <input
              type="text"
              value={formData.first_name}
              onChange={(e) => setFormData({...formData, first_name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cognome
            </label>
            <input
              type="text"
              value={formData.last_name}
              onChange={(e) => setFormData({...formData, last_name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={isEdit} // Email non modificabile in edit
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ruolo
            </label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="operator">Operatore</option>
              <option value="manager">Manager</option>
              <option value="admin">Amministratore</option>
            </select>
          </div>
          
          <div className="flex justify-end gap-2 pt-4">
            <button
              type="button"
              onClick={() => {
                if (isEdit) {
                  setShowEditForm(false);
                  setEditingUser(null);
                } else {
                  setShowCreateForm(false);
                }
                setFormData({ first_name: '', last_name: '', email: '', role: 'operator' });
              }}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Annulla
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? (isEdit ? 'Aggiornando...' : 'Creando...') : (isEdit ? 'Aggiorna' : 'Crea Utente')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Gestione Utenti</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          Nuovo Utente
        </button>
      </div>

      {showCreateForm && <UserForm />}
      {showEditForm && <UserForm isEdit={true} />}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Utente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ruolo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stato
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Azioni
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {user.first_name} {user.last_name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.role === 'admin' ? 'bg-red-100 text-red-800' :
                      user.role === 'manager' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Attivo' : 'Disattivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => startEdit(user)}
                        className="text-blue-600 hover:text-blue-900"
                        title="Modifica utente"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      
                      <button
                        onClick={() => toggleUserStatus(user)}
                        className={user.is_active ? 'text-yellow-600 hover:text-yellow-900' : 'text-green-600 hover:text-green-900'}
                        title={user.is_active ? 'Sospendi utente temporaneamente' : 'Attiva utente'}
                      >
                        {user.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                      </button>
                      
                      <button
                        onClick={() => deleteUser(user)}
                        className="text-orange-600 hover:text-orange-900"
                        title="Disattiva utente (reversibile)"
                      >
                        <UserX className="w-4 h-4" />
                      </button>
                      
                      <button
                        onClick={() => deleteUserPermanent(user)}
                        className="text-red-600 hover:text-red-900"
                        title="⚠️ CANCELLA DEFINITIVAMENTE (irreversibile)"
                      >
                        <AlertTriangle className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {loading && (
          <div className="text-center py-4">
            <div className="text-gray-500">Caricamento...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserManagement;
