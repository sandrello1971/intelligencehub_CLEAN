import React, { useState, useEffect } from 'react';
import { Plus, Calendar, Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import TaskCreateModal from './TaskCreateModal';
import TaskEditModal from './TaskEditModal';

interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed' | 'cancelled';
  assigned_to?: string;
  sla_deadline?: string;
  sla_status: 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED' | 'NO_SLA';
  priorita: 'bassa' | 'normale' | 'alta' | 'critica';
  created_at: string;
  sla_giorni?: number;
  warning_giorni: number;
  escalation_giorni: number;
  warning_deadline?: string;
  escalation_deadline?: string;
}

const TaskManagement: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(false);
  const [slaFilter, setSlaFilter] = useState<string>('');

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (slaFilter) params.append('sla_status', slaFilter);
      
      const response = await fetch(`/api/v1/tasks?${params.toString()}`);
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [slaFilter]);

  const getSlaStatusColor = (status: string) => {
    switch (status) {
      case 'GREEN': return 'bg-green-100 text-green-800 border-green-300';
      case 'YELLOW': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'ORANGE': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'RED': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getSlaStatusIcon = (status: string) => {
    switch (status) {
      case 'GREEN': return <CheckCircle className="w-4 h-4" />;
      case 'YELLOW': return <Clock className="w-4 h-4" />;
      case 'ORANGE': return <AlertTriangle className="w-4 h-4" />;
      case 'RED': return <AlertTriangle className="w-4 h-4" />;
      default: return null;
    }
  };

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'Non definita';
    return new Date(dateString).toLocaleString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Gestione Tasks</h1>
          <p className="text-gray-600">Sistema SLA a 3 livelli: Warning → Scadenza → Escalation</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Nuovo Task</span>
        </button>
      </div>

      <div className="mb-6 flex space-x-4">
        <button
          onClick={() => setSlaFilter('')}
          className={`px-4 py-2 rounded-lg border ${!slaFilter ? 'bg-blue-100 border-blue-300' : 'bg-white border-gray-300'}`}
        >
          Tutti
        </button>
        <button
          onClick={() => setSlaFilter('GREEN')}
          className={`px-4 py-2 rounded-lg border flex items-center space-x-2 ${slaFilter === 'GREEN' ? 'bg-green-100 border-green-300' : 'bg-white border-gray-300'}`}
        >
          <CheckCircle className="w-4 h-4 text-green-600" />
          <span>Nei Tempi</span>
        </button>
        <button
          onClick={() => setSlaFilter('YELLOW')}
          className={`px-4 py-2 rounded-lg border flex items-center space-x-2 ${slaFilter === 'YELLOW' ? 'bg-yellow-100 border-yellow-300' : 'bg-white border-gray-300'}`}
        >
          <Clock className="w-4 h-4 text-yellow-600" />
          <span>In Scadenza</span>
        </button>
        <button
          onClick={() => setSlaFilter('ORANGE')}
          className={`px-4 py-2 rounded-lg border flex items-center space-x-2 ${slaFilter === 'ORANGE' ? 'bg-orange-100 border-orange-300' : 'bg-white border-gray-300'}`}
        >
          <AlertTriangle className="w-4 h-4 text-orange-600" />
          <span>Scaduti</span>
        </button>
        <button
          onClick={() => setSlaFilter('RED')}
          className={`px-4 py-2 rounded-lg border flex items-center space-x-2 ${slaFilter === 'RED' ? 'bg-red-100 border-red-300' : 'bg-white border-gray-300'}`}
        >
          <AlertTriangle className="w-4 h-4 text-red-600" />
          <span>Critici</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Tasks Attivi</h2>
        </div>
        
        {loading ? (
          <div className="p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Caricamento...</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {tasks.map((task) => (
              <div key={task.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">{task.title}</h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getSlaStatusColor(task.sla_status)}`}>
                        {getSlaStatusIcon(task.sla_status)}
                        <span className="ml-1">{task.sla_status}</span>
                      </span>
                    </div>
                    
                    {task.description && (
                      <p className="text-gray-600 mb-3">{task.description}</p>
                    )}
                    
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Warning:</span>
                        <p className="text-gray-600">{formatDateTime(task.warning_deadline)}</p>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Scadenza:</span>
                        <p className="text-gray-600">{formatDateTime(task.sla_deadline)}</p>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Escalation:</span>
                        <p className="text-gray-600">{formatDateTime(task.escalation_deadline)}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setSelectedTask(task)}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      Modifica
                    </button>
                  </div>
                </div>
              </div>
            ))}
            
            {tasks.length === 0 && !loading && (
              <div className="p-6 text-center text-gray-500">
                Nessun task trovato
              </div>
            )}
          </div>
        )}
      </div>

      {showCreateModal && (
        <TaskCreateModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchTasks();
          }}
        />
      )}

      {selectedTask && (
        <TaskEditModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onSuccess={() => {
            setSelectedTask(null);
            fetchTasks();
          }}
        />
      )}
    </div>
  );
};

export default TaskManagement;
