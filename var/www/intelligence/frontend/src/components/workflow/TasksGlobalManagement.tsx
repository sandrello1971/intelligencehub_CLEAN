
import React, { useState, useEffect } from 'react';

const TasksGlobalManagement = () => {
  const [tasks, setTasks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [filterCategory, setFilterCategory] = useState('');
  
  const [newTask, setNewTask] = useState({
    tsk_code: '',
    tsk_description: '',
    tsk_type: 'standard',
    tsk_category: ''
  });

  const API_BASE = '/api/v1';

  const apiCall = async (url: string, options: RequestInit = {}) => {
    const token = localStorage.getItem("access_token");
    return fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
        ...options.headers
      }
    });
  };

  useEffect(() => {
    fetchTasks();
    fetchCategories();
  }, [filterCategory]);

  const fetchTasks = async () => {
    try {
      const url = filterCategory 
        ? `${API_BASE}/tasks-global/?category=${filterCategory}`
        : `${API_BASE}/tasks-global/`;
      const token = localStorage.getItem("access_token");
      const response = await fetch(url, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Errore nel caricamento');
      const data = await response.json();
      setTasks(data || []);
    } catch (error) {
      console.error('Errore:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`${API_BASE}/tasks-global/categories`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCategories(data || []);
      }
    } catch (error) {
      console.error('Errore caricamento categorie:', error);
    }
  };

  const createTask = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`${API_BASE}/tasks-global/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Errore nella creazione');
      }

      setIsCreateModalOpen(false);
      setNewTask({ tsk_code: '', tsk_description: '', tsk_type: 'standard', tsk_category: '' });
      alert('Task creato con successo!');
      fetchTasks();
      fetchCategories();
    } catch (error) {
      alert('Errore nella creazione: ' + error.message);
    }
  };

  const updateTask = async (e) => {
    e.preventDefault();
    if (!selectedTask) return;

    try {
      console.log("selectedTask.id:", selectedTask.id);
      console.log("selectedTask completo:", selectedTask);
      const response = await fetch(`${API_BASE}/tasks-global/${selectedTask.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tsk_code: selectedTask.tsk_code,
          tsk_description: selectedTask.tsk_description,
          tsk_type: selectedTask.tsk_type,
          tsk_category: selectedTask.tsk_category
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Errore nell\'aggiornamento');
      }

      setIsEditModalOpen(false);
      setSelectedTask(null);
      alert('Task aggiornato con successo!');
      fetchTasks();
      fetchCategories();
    } catch (error) {
      alert('Errore nell\'aggiornamento: ' + error.message);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      const response = await fetch(`${API_BASE}/tasks-global/${taskId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Errore nella cancellazione');
      
      alert('Task eliminato con successo!');
      fetchTasks();
    } catch (error) {
      alert('Errore nella cancellazione: ' + error.message);
    }
  };

  const openEditModal = (task) => {
    setSelectedTask({ ...task });
    setIsEditModalOpen(true);
  };

  const getCategoryColor = (category) => {
    const colors = {
      'setup': 'bg-blue-500 text-white',
      'development': 'bg-green-500 text-white',
      'testing': 'bg-yellow-500 text-white',
      'delivery': 'bg-purple-500 text-white',
      'admin': 'bg-gray-500 text-white'
    };
    return colors[category] || 'bg-gray-400 text-white';
  };

  const getTypeColor = (type) => {
    return type === 'standard' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Caricamento tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Gestione Tasks Globali</h1>
          <p className="text-gray-600">Configura i task standardizzati per i workflow</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors shadow-md"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span>Nuovo Task</span>
        </button>
      </div>

      {/* Filtri */}
      <div className="mb-6 flex space-x-4">
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tutte le categorie</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Totali</h3>
          <p className="text-3xl font-bold text-blue-600">{tasks.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Standard</h3>
          <p className="text-3xl font-bold text-green-600">{tasks.filter(t => t.tsk_type === 'standard').length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Custom</h3>
          <p className="text-3xl font-bold text-orange-600">{tasks.filter(t => t.tsk_type === 'custom').length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Categorie</h3>
          <p className="text-3xl font-bold text-purple-600">{categories.length}</p>
        </div>
      </div>

      {/* Tasks Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">Lista Tasks Globali</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Codice</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrizione</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoria</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Azioni</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tasks.map((task) => (
                <tr key={task.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-mono font-medium text-gray-900">{task.tsk_code}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{task.tsk_description}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {task.tsk_category && (
                      <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${getCategoryColor(task.tsk_category)}`}>
                        {task.tsk_category.toUpperCase()}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTypeColor(task.tsk_type)}`}>
                      {task.tsk_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button 
                        onClick={() => openEditModal(task)}
                        className="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1 rounded-md transition-colors"
                      >
                        Modifica
                      </button>
                      <button 
                        onClick={() => {
                          if (confirm(`Sei sicuro di voler eliminare il task ${task.tsk_code}?`)) {
                            deleteTask(task.id);
                          }
                        }}
                        className="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-3 py-1 rounded-md transition-colors"
                      >
                        Elimina
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Crea Nuovo Task</h3>
            </div>
            <form onSubmit={createTask}>
              <div className="px-6 py-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Codice Task *</label>
                  <input 
                    type="text" 
                    value={newTask.tsk_code}
                    onChange={(e) => setNewTask({...newTask, tsk_code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="es. SETUP001"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descrizione *</label>
                  <textarea 
                    value={newTask.tsk_description}
                    onChange={(e) => setNewTask({...newTask, tsk_description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Descrizione dettagliata del task"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
                  <input 
                    type="text" 
                    value={newTask.tsk_category}
                    onChange={(e) => setNewTask({...newTask, tsk_category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="es. setup, development, testing"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                  <select 
                    value={newTask.tsk_type}
                    onChange={(e) => setNewTask({...newTask, tsk_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="standard">Standard</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
              </div>
              <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
                <button 
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                >
                  Annulla
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                >
                  Crea Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {isEditModalOpen && selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Modifica Task: {selectedTask.tsk_code}</h3>
            </div>
            <form onSubmit={updateTask}>
              <div className="px-6 py-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Codice Task *</label>
                  <input 
                    type="text" 
                    value={selectedTask.tsk_code || ''}
                    onChange={(e) => setSelectedTask({...selectedTask, tsk_code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="es. SETUP001"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descrizione *</label>
                  <textarea 
                    value={selectedTask.tsk_description || ''}
                    onChange={(e) => setSelectedTask({...selectedTask, tsk_description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
                  <input 
                    type="text" 
                    value={selectedTask.tsk_category || ''}
                    onChange={(e) => setSelectedTask({...selectedTask, tsk_category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                  <select 
                    value={selectedTask.tsk_type || 'standard'}
                    onChange={(e) => setSelectedTask({...selectedTask, tsk_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="standard">Standard</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
              </div>
              <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
                <button 
                  type="button"
                  onClick={() => setIsEditModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                >
                  Annulla
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                >
                  Salva Modifiche
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TasksGlobalManagement;
