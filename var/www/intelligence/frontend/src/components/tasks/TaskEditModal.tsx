import React, { useState } from 'react';
import { X, Calendar, Clock, AlertTriangle, Trash2 } from 'lucide-react';

interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed' | 'cancelled';
  priorita: 'bassa' | 'normale' | 'alta' | 'critica';
  sla_giorni?: number;
  warning_giorni: number;
  escalation_giorni: number;
  sla_deadline?: string;
  warning_deadline?: string;
  escalation_deadline?: string;
  estimated_hours?: number;
  actual_hours?: number;
}

interface TaskEditModalProps {
  task: Task;
  onClose: () => void;
  onSuccess: () => void;
}

const TaskEditModal: React.FC<TaskEditModalProps> = ({ task, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: task.title,
    description: task.description || '',
    status: task.status,
    priorita: task.priorita,
    sla_giorni: task.sla_giorni || 5,
    warning_giorni: task.warning_giorni,
    escalation_giorni: task.escalation_giorni,
    estimated_hours: task.estimated_hours || '',
    actual_hours: task.actual_hours || ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = {
        title: formData.title,
        description: formData.description,
        status: formData.status,
        priorita: formData.priorita,
        sla_giorni: formData.sla_giorni,
        warning_giorni: formData.warning_giorni,
        escalation_giorni: formData.escalation_giorni,
        estimated_hours: formData.estimated_hours ? parseFloat(formData.estimated_hours.toString()) : null,
        actual_hours: formData.actual_hours ? parseFloat(formData.actual_hours.toString()) : null
      };

      const response = await fetch(`/api/v1/tasks/${task.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        onSuccess();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Errore durante l\'aggiornamento del task');
      }
    } catch (err) {
      setError('Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">Modifica Task</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Titolo Task *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Descrizione</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as any }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Corso</option>
                  <option value="completed">Completato</option>
                  <option value="cancelled">Annullato</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priorità</label>
                <select
                  value={formData.priorita}
                  onChange={(e) => setFormData(prev => ({ ...prev, priorita: e.target.value as any }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="bassa">Bassa</option>
                  <option value="normale">Normale</option>
                  <option value="alta">Alta</option>
                  <option value="critica">Critica</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">SLA (giorni)</label>
                <input
                  type="number"
                  min="1"
                  value={formData.sla_giorni}
                  onChange={(e) => setFormData(prev => ({ ...prev, sla_giorni: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Warning (giorni)</label>
                <input
                  type="number"
                  min="0"
                  value={formData.warning_giorni}
                  onChange={(e) => setFormData(prev => ({ ...prev, warning_giorni: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Escalation (giorni)</label>
                <input
                  type="number"
                  min="0"
                  value={formData.escalation_giorni}
                  onChange={(e) => setFormData(prev => ({ ...prev, escalation_giorni: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Annulla
            </button>
            <button
              type="submit"
              disabled={loading || !formData.title}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Aggiornamento...' : 'Aggiorna Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskEditModal;
