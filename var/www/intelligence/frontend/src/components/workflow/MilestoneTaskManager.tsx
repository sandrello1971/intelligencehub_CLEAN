import React, { useState, useEffect } from 'react';

// Mock del servizio API - sostituire con import reale
const workflowApi = {
  async getMilestoneTasks(milestoneId: number) {
    const response = await fetch(`/api/v1/admin/milestone-templates/${milestoneId}/tasks`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    return { success: response.ok, data };
  },
  
  async reorderMilestoneTasks(milestoneId: number, tasksOrder: any[]) {
    const response = await fetch(`/api/v1/admin/milestone-templates/${milestoneId}/tasks/reorder`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ tasks_order: tasksOrder })
    });
    const data = await response.json();
    return { success: response.ok, data };
  }
};

interface TaskTemplate {
  id: number;
  milestone_id: number;
  nome: string;
  descrizione: string;
  ordine: number;
  durata_stimata_ore: number;
  ruolo_responsabile: string;
  obbligatorio: boolean;
  tipo_task: string;
}

interface MilestoneTaskManagerProps {
  milestoneId: number;
  milestoneName: string;
  open: boolean;
  onClose: () => void;
  onTasksUpdated?: () => void;
}

const MilestoneTaskManager: React.FC<MilestoneTaskManagerProps> = ({
  milestoneId,
  milestoneName,
  open,
  onClose,
  onTasksUpdated
}) => {
  const [tasks, setTasks] = useState<TaskTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [milestoneInfo, setMilestoneInfo] = useState<{
    sla_giorni: number;
    total_hours: number;
  } | null>(null);

  useEffect(() => {
    if (open && milestoneId) {
      loadTasks();
    }
  }, [open, milestoneId]);

  const loadTasks = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await workflowApi.getMilestoneTasks(milestoneId);
      
      if (result.success && result.data) {
        setTasks(result.data.tasks || []);
        setMilestoneInfo({
          sla_giorni: result.data.milestone_sla_giorni,
          total_hours: result.data.total_hours
        });
      } else {
        setError('Errore caricamento task');
      }
    } catch (err) {
      setError('Errore di connessione');
      console.error('Errore caricamento task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTasksReorder = async (reorderedTasks: TaskTemplate[]) => {
    setLoading(true);
    setError(null);
    
    try {
      const tasksOrder = reorderedTasks.map(task => ({
        id: task.id,
        ordine: task.ordine
      }));
      
      const result = await workflowApi.reorderMilestoneTasks(milestoneId, tasksOrder);
      
      if (result.success) {
        setTasks(reorderedTasks);
        setSuccess(`Ordine aggiornato per ${result.data?.updated_tasks || 0} task`);
        setHasChanges(false);
        
        if (onTasksUpdated) {
          onTasksUpdated();
        }
        
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError('Errore salvataggio ordine');
      }
    } catch (err) {
      setError('Errore di connessione');
      console.error('Errore salvataggio ordine:', err);
    } finally {
      setLoading(false);
    }
  };

  const moveTask = (taskId: number, direction: 'up' | 'down') => {
    const taskIndex = tasks.findIndex(t => t.id === taskId);
    if (taskIndex === -1) return;

    const newTasks = [...tasks];
    
    if (direction === 'up' && taskIndex > 0) {
      [newTasks[taskIndex], newTasks[taskIndex - 1]] = [newTasks[taskIndex - 1], newTasks[taskIndex]];
    } else if (direction === 'down' && taskIndex < newTasks.length - 1) {
      [newTasks[taskIndex], newTasks[taskIndex + 1]] = [newTasks[taskIndex + 1], newTasks[taskIndex]];
    }

    newTasks.forEach((task, index) => {
      task.ordine = index + 1;
    });

    setTasks(newTasks);
    setHasChanges(true);
  };

  const handleSaveOrder = () => {
    handleTasksReorder(tasks);
  };

  const handleResetOrder = () => {
    loadTasks();
    setHasChanges(false);
  };

  if (!open) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '800px',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
      }}>
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#f8f9fa',
          borderRadius: '12px 12px 0 0'
        }}>
          <h2 style={{ margin: 0, color: '#1976d2', fontSize: '1.4rem' }}>
            📋 Ordine Task: {milestoneName}
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#666',
              padding: '4px',
              borderRadius: '4px'
            }}
          >
            ✕
          </button>
        </div>

        <div style={{ padding: '24px' }}>
          {/* Info */}
          {milestoneInfo && (
            <div style={{
              background: '#e3f2fd',
              padding: '16px',
              borderRadius: '8px',
              marginBottom: '20px',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <strong>📊 {tasks.length} Task - {milestoneInfo.total_hours}h - {milestoneInfo.sla_giorni} giorni</strong>
              {hasChanges && (
                <div>
                  <button
                    onClick={handleSaveOrder}
                    style={{
                      background: '#2e7d32',
                      color: 'white',
                      border: 'none',
                      padding: '8px 16px',
                      borderRadius: '4px',
                      marginRight: '8px',
                      cursor: 'pointer'
                    }}
                  >
                    💾 Salva
                  </button>
                  <button
                    onClick={handleResetOrder}
                    style={{
                      background: '#666',
                      color: 'white',
                      border: 'none',
                      padding: '8px 16px',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    ❌ Annulla
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Messages */}
          {success && (
            <div style={{
              background: '#d4edda',
              color: '#155724',
              padding: '12px',
              borderRadius: '4px',
              marginBottom: '16px'
            }}>
              ✅ {success}
            </div>
          )}

          {error && (
            <div style={{
              background: '#f8d7da',
              color: '#721c24',
              padding: '12px',
              borderRadius: '4px',
              marginBottom: '16px'
            }}>
              ❌ {error}
            </div>
          )}

          {/* Task List */}
          {tasks.map((task, index) => (
            <div key={task.id} style={{
              display: 'flex',
              alignItems: 'center',
              padding: '16px',
              border: hasChanges ? '2px dashed #1976d2' : '1px solid #e0e0e0',
              borderRadius: '8px',
              marginBottom: '8px',
              background: hasChanges ? 'rgba(25, 118, 210, 0.04)' : 'white'
            }}>
              {/* Order */}
              <div style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: '#1976d2',
                width: '40px',
                textAlign: 'center',
                marginRight: '16px'
              }}>
                {task.ordine}
              </div>

              {/* Content */}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <strong>{task.nome}</strong>
                  <span style={{
                    background: task.tipo_task === 'generale' ? '#1976d2' : '#666',
                    color: 'white',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontSize: '11px'
                  }}>
                    {task.tipo_task}
                  </span>
                </div>
                <div style={{ color: '#666', fontSize: '14px', marginBottom: '4px' }}>
                  {task.descrizione}
                </div>
                <div style={{ fontSize: '12px', color: '#999' }}>
                  ⏱️ {task.durata_stimata_ore}h {task.ruolo_responsabile && `👤 ${task.ruolo_responsabile}`}
                </div>
              </div>

              {/* Actions */}
              <div>
                <button
                  onClick={() => moveTask(task.id, 'up')}
                  disabled={index === 0}
                  style={{
                    background: 'none',
                    border: 'none',
                    fontSize: '18px',
                    cursor: index === 0 ? 'not-allowed' : 'pointer',
                    opacity: index === 0 ? 0.3 : 1,
                    padding: '4px'
                  }}
                >
                  ⬆️
                </button>
                <button
                  onClick={() => moveTask(task.id, 'down')}
                  disabled={index === tasks.length - 1}
                  style={{
                    background: 'none',
                    border: 'none',
                    fontSize: '18px',
                    cursor: index === tasks.length - 1 ? 'not-allowed' : 'pointer',
                    opacity: index === tasks.length - 1 ? 0.3 : 1,
                    padding: '4px'
                  }}
                >
                  ⬇️
                </button>
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              Caricamento...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MilestoneTaskManager;
