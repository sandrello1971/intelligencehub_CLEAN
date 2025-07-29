import React, { useState, useEffect } from 'react';

interface ModelloTicket {
  id: string;
  nome: string;
  descrizione: string;
  workflow_template_id: number | null;
  priority: string;
  is_active: boolean;
}

interface Workflow {
  id: number;
  nome: string;
  descrizione: string;
  milestones?: any[];
}

const ModelliTicket: React.FC = () => {
  const [modelli, setModelli] = useState<ModelloTicket[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    nome: '',
    descrizione: '',
    workflow_template_id: '',
    priority: "medium"
  });
  const [editingModel, setEditingModel] = useState<any>(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const [calculatedSLA, setCalculatedSLA] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (formData.workflow_template_id) {
      calculateSLA(parseInt(formData.workflow_template_id));
    } else {
      setCalculatedSLA(null);
    }
  }, [formData.workflow_template_id, workflows]);

  const calculateSLA = async (workflowId: number) => {
    try {
      const response = await fetch(`/api/v1/admin/workflow-config/workflow-templates/${workflowId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const workflow = await response.json();
        let totalHours = 0;
        
        if (workflow.milestones) {
          workflow.milestones.forEach((milestone: any) => {
            if (milestone.task_templates) {
              milestone.task_templates.forEach((task: any) => {
                totalHours += task.durata_stimata_ore || 0;
              });
            }
          });
        }
        
        const totalDays = Math.round((totalHours / 8) * 10) / 10;
        setCalculatedSLA(totalDays > 0 ? totalDays : null);
      }
    } catch (error) {
      console.error('Errore calcolo SLA:', error);
      setCalculatedSLA(null);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadModelli(),
        loadWorkflows()
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadModelli = async () => {
    try {
      const response = await fetch('/api/v1/templates/ticket-templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setModelli(data);
      }
    } catch (error) {
      console.error('Errore caricamento modelli:', error);
    }
  };

  const loadWorkflows = async () => {
    try {
      const response = await fetch('/api/v1/admin/workflow-config/workflow-templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setWorkflows(data);
      }
    } catch (error) {
      console.error('Errore caricamento workflow:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const payload = {
        nome: formData.nome,
        descrizione: formData.descrizione,
        workflow_template_id: formData.workflow_template_id ? parseInt(formData.workflow_template_id) : null,
        priority: formData.priority,
        is_active: true
      };

      const response = await fetch('/api/v1/templates/ticket-templates', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        alert('Modello ticket creato con successo!');
        setShowForm(false);
        setFormData({
          nome: '',
          descrizione: '',
          workflow_template_id: '',
          priority: "medium"
        });
        setCalculatedSLA(null);
        loadModelli();
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail || 'Impossibile creare modello'}`);
      }
    } catch (error) {
      console.error('Errore creazione:', error);
      alert('Errore di connessione');
    }
  };

  const handleEditModel = (modello: ModelloTicket) => {
    setEditingModel(modello);
    setFormData({
      nome: modello.nome,
      descrizione: modello.descrizione || "",
      workflow_template_id: modello.workflow_template_id ? modello.workflow_template_id.toString() : "",
      priority: modello.priority
    });
    setShowEditForm(true);
    setShowForm(false);
  };

  const handleUpdateModel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingModel) return;
    
    try {
      const payload = {
        nome: formData.nome,
        descrizione: formData.descrizione,
        workflow_template_id: formData.workflow_template_id ? parseInt(formData.workflow_template_id) : null,
        priority: formData.priority,
      };

      const response = await fetch(`/api/v1/templates/ticket-templates/${editingModel.id}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        alert("Modello aggiornato con successo!");
        setShowEditForm(false);
        setEditingModel(null);
        setFormData({ nome: "", descrizione: "", workflow_template_id: "", priority: "medium" });
        setCalculatedSLA(null);
        loadModelli();
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail || "Impossibile aggiornare modello"}`);
      }
    } catch (error) {
      console.error("Errore aggiornamento:", error);
      alert("Errore di connessione");
    }
  };

  const handleDeleteModel = async (modelId: string) => {
    if (!confirm("Sei sicuro di voler disattivare questo modello?")) return;
    
    try {
      const response = await fetch(`/api/v1/templates/ticket-templates/${modelId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        }
      });

      if (response.ok) {
        alert("Modello disattivato con successo!");
        loadModelli();
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail || "Impossibile eliminare modello"}`);
      }
    } catch (error) {
      console.error("Errore eliminazione:", error);
      alert("Errore di connessione");
    }
  };

  const handleActivateModel = async (modelId: string) => {
    try {
      const response = await fetch(`/api/v1/templates/ticket-templates/${modelId}/activate`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        }
      });

      if (response.ok) {
        alert("Modello riattivato con successo!");
        loadModelli();
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail || "Impossibile riattivare modello"}`);
      }
    } catch (error) {
      console.error("Errore riattivazione:", error);
      alert("Errore di connessione");
    }
  };

  const getWorkflowNome = (id: number | null) => {
    if (!id) return 'Nessuno';
    const workflow = workflows.find(w => w.id === id);
    return workflow ? workflow.nome : 'N/A';
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Caricamento...</div>;
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1>Modelli Ticket</h1>
          <p>Gestione template per la creazione automatica di ticket</p>
        </div>
        <button 
          onClick={() => setShowForm(!showForm)}
          style={{
            background: '#4CAF50',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          {showForm ? 'Annulla' : '+ Nuovo Modello'}
        </button>
      </div>

      {showForm && (
        <div style={{
          background: '#f9f9f9',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #ddd'
        }}>
          <h3>Nuovo Modello Ticket</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px' }}>
              <div>
                <label>Nome Modello *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                  style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                  required
                />
              </div>
              
              <div>
                <label>Priorità</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({...formData, priority: e.target.value})}
                  style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                >
                  <option value="bassa">Bassa</option>
                  <option value="medium">Media</option>
                  <option value="alta">Alta</option>
                  <option value="urgente">Urgente</option>
                </select>
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <label>Workflow Associato</label>
                <select
                  value={formData.workflow_template_id}
                  onChange={(e) => setFormData({...formData, workflow_template_id: e.target.value})}
                  style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                >
                  <option value="">Nessun workflow</option>
                  {workflows.map(workflow => (
                    <option key={workflow.id} value={workflow.id}>
                      {workflow.nome}
                    </option>
                  ))}
                </select>
                {calculatedSLA && (
                  <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                    SLA calcolato: {calculatedSLA} giorni lavorativi
                  </p>
                )}
              </div>
            </div>

            <div style={{ marginTop: '15px' }}>
              <label>Descrizione</label>
              <textarea
                value={formData.descrizione}
                onChange={(e) => setFormData({...formData, descrizione: e.target.value})}
                style={{ width: '100%', padding: '8px', marginTop: '5px', height: '80px' }}
                placeholder="Descrizione del modello ticket..."
              />
            </div>

            <div style={{ marginTop: '20px' }}>
              <button 
                type="submit"
                style={{
                  background: '#2196F3',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  marginRight: '10px'
                }}
              >
                Crea Modello
              </button>
              <button 
                type="button"
                onClick={() => setShowForm(false)}
                style={{
                  background: '#f44336',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Annulla
              </button>
            </div>
          </form>
        </div>
      )}


      {showEditForm && (
        <div style={{
          background: "#f0f8ff",
          padding: "20px",
          borderRadius: "8px",
          marginBottom: "20px",
          border: "2px solid #2196F3"
        }}>
          <h3>Modifica Modello Ticket</h3>
          <form onSubmit={handleUpdateModel}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px", marginTop: "15px" }}>
              <div>
                <label>Nome Modello *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                  style={{ width: "100%", padding: "8px", marginTop: "5px" }}
                  required
                />
              </div>
              
              <div>
                <label>Priorità</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({...formData, priority: e.target.value})}
                  style={{ width: "100%", padding: "8px", marginTop: "5px" }}
                >
                  <option value="bassa">Bassa</option>
                  <option value="medium">Media</option>
                  <option value="alta">Alta</option>
                  <option value="urgente">Urgente</option>
                </select>
              </div>

              <div style={{ gridColumn: "span 2" }}>
                <label>Workflow Associato</label>
                <select
                  value={formData.workflow_template_id}
                  onChange={(e) => setFormData({...formData, workflow_template_id: e.target.value})}
                  style={{ width: "100%", padding: "8px", marginTop: "5px" }}
                >
                  <option value="">Nessun workflow</option>
                  {workflows.map(workflow => (
                    <option key={workflow.id} value={workflow.id}>
                      {workflow.nome}
                    </option>
                  ))}
                </select>
                {calculatedSLA && (
                  <p style={{ fontSize: "12px", color: "#666", marginTop: "5px" }}>
                    SLA calcolato: {calculatedSLA} giorni lavorativi
                  </p>
                )}
              </div>
            </div>

            <div style={{ marginTop: "15px" }}>
              <label>Descrizione</label>
              <textarea
                value={formData.descrizione}
                onChange={(e) => setFormData({...formData, descrizione: e.target.value})}
                style={{ width: "100%", padding: "8px", marginTop: "5px", height: "80px" }}
                placeholder="Descrizione del modello ticket..."
              />
            </div>

            <div style={{ marginTop: "20px" }}>
              <button 
                type="submit"
                style={{
                  background: "#2196F3",
                  color: "white",
                  border: "none",
                  padding: "10px 20px",
                  borderRadius: "6px",
                  cursor: "pointer",
                  marginRight: "10px"
                }}
              >
                💾 Aggiorna Modello
              </button>
              <button 
                type="button"
                onClick={() => {
                  setShowEditForm(false);
                  setEditingModel(null);
                  setFormData({ nome: "", descrizione: "", workflow_template_id: "", priority: "medium" });
                  setCalculatedSLA(null);
                }}
                style={{
                  background: "#f44336",
                  color: "white",
                  border: "none",
                  padding: "10px 20px",
                  borderRadius: "6px",
                  cursor: "pointer"
                }}
              >
                Annulla
              </button>
            </div>
          </form>
        </div>
      )}
      <div style={{ marginTop: '20px' }}>
        <h3>Modelli Configurati ({modelli.length})</h3>
        
        {modelli.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic' }}>
            Nessun modello ticket configurato. Crea il primo modello per iniziare!
          </p>
        ) : (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', 
            gap: '15px',
            marginTop: '15px'
          }}>
            {modelli.map(modello => (
              <div key={modello.id} style={{
                background: 'white',
                padding: '15px',
                borderRadius: '8px',
                border: '1px solid #ddd',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}>
                <h4 style={{ marginBottom: '10px', color: '#333' }}>{modello.nome}</h4>
                <p style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                  {modello.descrizione || 'Nessuna descrizione'}
                </p>
                
                <div style={{ fontSize: '12px', color: '#555' }}>
                  <div><strong>Workflow:</strong> {getWorkflowNome(modello.workflow_template_id)}</div>
                  <div><strong>Priorità:</strong> {modello.priority}</div>
                  <div><strong>Stato:</strong> {modello.is_active ? 'Attivo' : 'Disattivo'}</div>
                </div>
                
                <div style={{ marginTop: "15px", display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                  <button
                    onClick={() => handleEditModel(modello)}
                    style={{
                      background: "#2196F3",
                      color: "white",
                      border: "none",
                      padding: "6px 12px",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontSize: "12px"
                    }}
                  >
                    ✏️ Modifica
                  </button>
                  <button
                    onClick={() => handleDeleteModel(modello.id)}
                    style={{
                      background: "#f44336",
                      color: "white",
                      border: "none",
                      padding: "6px 12px",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontSize: "12px"
                    }}
                  >
                    🗑️ Elimina
                  </button>
                  {!modello.is_active && (
                    <button
                      onClick={() => handleActivateModel(modello.id)}
                      style={{
                        background: "#4CAF50",
                        color: "white",
                        border: "none",
                        padding: "6px 12px",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "12px"
                      }}
                    >
                      ✅ Riattiva
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ModelliTicket;
