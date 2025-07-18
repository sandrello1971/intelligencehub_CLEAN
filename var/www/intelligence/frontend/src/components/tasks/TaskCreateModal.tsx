import React, { useState } from 'react';
import { X, Calendar, Clock, AlertTriangle } from 'lucide-react';

interface TaskCreateModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

interface TaskFormData {
  title: string;
  description: string;
  sla_giorni: number;
  warning_giorni: number;
  escalation_giorni: number;
  priorita: 'bassa' | 'normale' | 'alta' | 'critica';
  useManualSLA: boolean;
  sla_deadline: string;
  warning_deadline: string;
  escalation_deadline: string;
}

const TaskCreateModal: React.FC<TaskCreateModalProps> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: '',
    description: '',
    sla_giorni: 5,
    warning_giorni: 1,
    escalation_giorni: 1,
    priorita: 'normale',
    useManualSLA: false,
    sla_deadline: '',
    warning_deadline: '',
    escalation_deadline: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload: any = {
        title: formData.title,
        description: formData.description,
        priorita: formData.priorita
      };

      if (formData.useManualSLA) {
        if (formData.sla_deadline) payload.sla_deadline = formData.sla_deadline;
        if (formData.warning_deadline) payload.warning_deadline = formData.warning_deadline;
        if (formData.escalation_deadline) payload.escalation_deadline = formData.escalation_deadline;
      } else {
        payload.sla_giorni = formData.sla_giorni;
        payload.warning_giorni = formData.warning_giorni;
        payload.escalation_giorni = formData.escalation_giorni;
      }

      const response = await fetch('/api/v1/tasks-global/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        onSuccess();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Errore durante la creazione del task');
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
          <h2 className="text-xl font-semibold text-gray-900">Nuovo Task con SLA</h2>
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
            <h3 className="text-lg font-medium text-gray-900">Informazioni Base</h3>
            
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

          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Configurazione SLA</h3>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Clock className="w-4 h-4 inline mr-1" />
                  SLA Totale (giorni)
                </label>
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={formData.sla_giorni}
                  onChange={(e) => setFormData(prev => ({ ...prev, sla_giorni: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <AlertTriangle className="w-4 h-4 inline mr-1 text-yellow-500" />
                  Warning (giorni prima)
                </label>
                <input
                  type="number"
                  min="0"
                  max="30"
                  value={formData.warning_giorni}
                  onChange={(e) => setFormData(prev => ({ ...prev, warning_giorni: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <AlertTriangle className="w-4 h-4 inline mr-1 text-red-500" />
                  Escalation (giorni dopo)
                </label>
                <input
                  type="number"
                  min="0"
                  max="30"
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
              {loading ? 'Creazione...' : 'Crea Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskCreateModal;
