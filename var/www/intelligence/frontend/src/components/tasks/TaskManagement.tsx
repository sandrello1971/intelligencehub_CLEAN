import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Code, Clock, Save, X } from 'lucide-react';

interface TaskModel {
  id: number;
  tsk_code: string;
  tsk_description?: string;
  tsk_type: string;
  tsk_category?: string;
  sla_giorni?: number;
  warning_giorni: number;
  escalation_giorni: number;
  priorita: string;
  created_at: string;
}

interface TaskModelForm {
  tsk_code: string;
  tsk_description: string;
  tsk_type: string;
  tsk_category: string;
  sla_giorni: number;
  warning_giorni: number;
  escalation_giorni: number;
  priorita: string;
}

const TaskManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'models' | 'operational'>('models');
  const [tasks, setTasks] = useState<TaskModel[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState<TaskModel | null>(null);
  const [loading, setLoading] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [formData, setFormData] = useState<TaskModelForm>({
    tsk_code: '',
    tsk_description: '',
    tsk_type: 'template',
    tsk_category: 'generale',
    sla_giorni: 3,
    warning_giorni: 1,
    escalation_giorni: 1,
    priorita: 'normale'
  });

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (categoryFilter) params.append('category', categoryFilter);
      
      const response = await fetch(`/api/v1/tasks-global/?${params.toString()}`);
      const data = await response.json();
      console.log('Fetched tasks:', data); // Debug log spostato qui
      setTasks(data);
    } catch (error) {
      console.error('Error fetching task models:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const url = selectedTask 
        ? `/api/v1/tasks-global/${selectedTask.id}`
        : '/api/v1/tasks-global/';
      
      const method = selectedTask ? 'PUT' : 'POST';

      // Assicurati che sla_giorni sia un numero valido
      const submitData = {
        ...formData,
        sla_giorni: Number(formData.sla_giorni) || 3,
        warning_giorni: Number(formData.warning_giorni) || 1,
        escalation_giorni: Number(formData.escalation_giorni) || 1
      };

      console.log('Submitting data:', submitData); // Debug log

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(submitData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Errore nel salvataggio: ${errorText}`);
      }

      alert(selectedTask ? 'Modello aggiornato!' : 'Modello creato!');
      setShowCreateModal(false);
      setSelectedTask(null);
      resetForm();
      fetchTasks();
    } catch (error) {
      console.error('Submit error:', error);
      alert('Errore: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId: number) => {
    try {
      const response = await fetch(`/api/v1/tasks-global/${taskId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Errore nella cancellazione');
      
      alert('Modello eliminato con successo!');
      fetchTasks();
    } catch (error) {
      alert('Errore nella cancellazione: ' + error.message);
    }
  };

  const resetForm = () => {
    setFormData({
      tsk_code: '',
      tsk_description: '',
      tsk_type: 'template',
      tsk_category: 'generale',
      sla_giorni: 3,
      warning_giorni: 1,
      escalation_giorni: 1,
      priorita: 'normale'
    });
  };

  const openEditModal = (task: TaskModel) => {
    console.log('Opening edit modal for task:', task); // Debug log
    setSelectedTask(task);
    setFormData({
      tsk_code: task.tsk_code,
      tsk_description: task.tsk_description || '',
      tsk_type: task.tsk_type,
      tsk_category: task.tsk_category || 'generale',
      sla_giorni: task.sla_giorni || 3,
      warning_giorni: task.warning_giorni,
      escalation_giorni: task.escalation_giorni,
      priorita: task.priorita
    });
    setShowCreateModal(true);
  };

  const openCreateModal = () => {
    setSelectedTask(null);
    resetForm();
    setShowCreateModal(true);
  };

  useEffect(() => {
    if (activeTab === 'models') {
      fetchTasks();
    }
  }, [activeTab, categoryFilter]);

  const getPriorityColor = (priorita: string) => {
    switch (priorita) {
      case 'bassa': return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'normale': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'alta': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'critica': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'template': return 'bg-purple-100 text-purple-800';
      case 'standard': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Gestione Tasks con SLA</h1>
          <p className="text-gray-600">Sistema completo per modelli task e task operativi</p>
        </div>
        <button
          onClick={openCreateModal}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Nuovo Modello</span>
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('models')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'models'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Modelli Task
          </button>
          <button
            onClick={() => setActiveTab('operational')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'operational'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Task Operativi
          </button>
        </nav>
      </div>

      {/* Filtri */}
      {activeTab === 'models' && (
        <div className="mb-6 flex space-x-4">
          <button
            onClick={() => setCategoryFilter('')}
            className={`px-4 py-2 rounded-lg border ${!categoryFilter ? 'bg-blue-100 border-blue-300' : 'bg-white border-gray-300'}`}
          >
            Tutti
          </button>
          <button
            onClick={() => setCategoryFilter('setup')}
            className={`px-4 py-2 rounded-lg border ${categoryFilter === 'setup' ? 'bg-blue-100 border-blue-300' : 'bg-white border-gray-300'}`}
          >
            Setup
          </button>
          <button
            onClick={() => setCategoryFilter('generale')}
            className={`px-4 py-2 rounded-lg border ${categoryFilter === 'generale' ? 'bg-blue-100 border-blue-300' : 'bg-white border-gray-300'}`}
          >
            Generale
          </button>
        </div>
      )}

      {/* Content */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {activeTab === 'models' ? 'Modelli Task Disponibili' : 'Task Operativi Attivi'}
          </h2>
        </div>
        
        {activeTab === 'models' ? (
          loading ? (
            <div className="p-6 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Caricamento...</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {tasks.map((task) => {
                // Debug log spostato fuori dal JSX
                console.log("Task SLA debug:", task.sla_giorni, task);
                
                return (
                  <div key={task.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <div className="flex items-center space-x-2">
                            <Code className="w-5 h-5 text-gray-500" />
                            <h3 className="text-lg font-medium text-gray-900">{task.tsk_code}</h3>
                          </div>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(task.tsk_type)}`}>
                            {task.tsk_type}
                          </span>
                          {task.tsk_category && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              {task.tsk_category}
                            </span>
                          )}
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getPriorityColor(task.priorita)}`}>
                            {task.priorita}
                          </span>
                        </div>
                        
                        {task.tsk_description && (
                          <p className="text-gray-600 mb-3">{task.tsk_description}</p>
                        )}
                        
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div className="flex items-center space-x-2">
                            <Clock className="w-4 h-4 text-blue-500" />
                            <div>
                              <span className="font-medium text-gray-700">SLA Totale:</span>
                              <p className="text-gray-600">
                                {task.sla_giorni !== undefined && task.sla_giorni !== null 
                                  ? `${task.sla_giorni} giorni` 
                                  : 'Non definito'
                                }
                              </p>
                            </div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Warning:</span>
                            <p className="text-gray-600">{task.warning_giorni} giorni prima</p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Escalation:</span>
                            <p className="text-gray-600">{task.escalation_giorni} giorni dopo</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2">
                        <button
                          onClick={() => openEditModal(task)}
                          className="text-blue-600 hover:text-blue-800 font-medium px-3 py-1 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors flex items-center space-x-1"
                        >
                          <Edit className="w-4 h-4" />
                          <span>Modifica</span>
                        </button>
                        <button
                          onClick={() => {
                            if (confirm(`Sei sicuro di voler eliminare il modello "${task.tsk_code}"?`)) {
                              deleteTask(task.id);
                            }
                          }}
                          className="text-red-600 hover:text-red-800 font-medium px-3 py-1 bg-red-50 hover:bg-red-100 rounded-md transition-colors flex items-center space-x-1"
                        >
                          <Trash2 className="w-4 h-4" />
                          <span>Elimina</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
              
              {tasks.length === 0 && !loading && (
                <div className="p-6 text-center text-gray-500">
                  <Code className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p>Nessun modello task trovato</p>
                  <p className="text-sm">Crea il primo modello per iniziare</p>
                </div>
              )}
            </div>
          )
        ) : (
          <div className="p-6 text-center text-gray-500">
            <p>Task operativi - Funzionalità da implementare</p>
            <p className="text-sm">Qui verranno mostrati i task reali creati dai modelli</p>
          </div>
        )}
      </div>

      {/* Modal Creazione/Modifica */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">
                {selectedTask ? 'Modifica Modello Task' : 'Nuovo Modello Task'}
              </h2>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setSelectedTask(null);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Codice Task *
                  </label>
                  <input
                    type="text"
                    value={formData.tsk_code}
                    onChange={(e) => setFormData({...formData, tsk_code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="TSK_CODICE_TASK"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo
                  </label>
                  <select
                    value={formData.tsk_type}
                    onChange={(e) => setFormData({...formData, tsk_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="template">Template</option>
                    <option value="standard">Standard</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descrizione
                </label>
                <textarea
                  value={formData.tsk_description}
                  onChange={(e) => setFormData({...formData, tsk_description: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Descrizione dettagliata del task..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Categoria
                  </label>
                  <select
                    value={formData.tsk_category}
                    onChange={(e) => setFormData({...formData, tsk_category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="generale">Generale</option>
                    <option value="setup">Setup</option>
                    <option value="delivery">Delivery</option>
                    <option value="support">Support</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priorità
                  </label>
                  <select
                    value={formData.priorita}
                    onChange={(e) => setFormData({...formData, priorita: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="bassa">Bassa</option>
                    <option value="normale">Normale</option>
                    <option value="alta">Alta</option>
                    <option value="critica">Critica</option>
                  </select>
                </div>
              </div>

              <div className="border-t pt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Configurazione SLA</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      SLA Totale (giorni) *
                    </label>
                    <input
                      type="number"
                      value={formData.sla_giorni}
                      onChange={(e) => {
                        const value = parseInt(e.target.value) || 3;
                        setFormData({...formData, sla_giorni: value});
                      }}
                      min="1"
                      max="365"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">Giorni totali per completare il task</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Warning (giorni prima)
                    </label>
                    <input
                      type="number"
                      value={formData.warning_giorni}
                      onChange={(e) => {
                        const value = parseInt(e.target.value) || 1;
                        setFormData({...formData, warning_giorni: value});
                      }}
                      min="0"
                      max="30"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Avviso prima della scadenza</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Escalation (giorni dopo)
                    </label>
                    <input
                      type="number"
                      value={formData.escalation_giorni}
                      onChange={(e) => {
                        const value = parseInt(e.target.value) || 1;
                        setFormData({...formData, escalation_giorni: value});
                      }}
                      min="0"
                      max="30"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Escalation dopo scadenza</p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    setSelectedTask(null);
                    resetForm();
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                >
                  Annulla
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors flex items-center space-x-2 disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  <span>{loading ? 'Salvando...' : (selectedTask ? 'Aggiorna' : 'Crea')}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskManagement;
