import React, { useState, useEffect } from 'react';

interface ModelloTicket {
  id: string;
  nome: string;
  descrizione: string;
  articolo_id: number | null;
  workflow_template_id: number | null;
  priority: string;
  sla_hours: number;
  is_active: boolean;
}

interface Articolo {
  id: number;
  codice: string;
  nome: string;
}

interface Workflow {
  id: number;
  nome: string;
  descrizione: string;
  milestones?: any[];
}

const ModelliTicket: React.FC = () => {
  const [modelli, setModelli] = useState<ModelloTicket[]>([]);
  const [articoli, setArticoli] = useState<Articolo[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    nome: '',
    descrizione: '',
    articolo_id: '',
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
      // Carica il workflow completo con milestone e task
      const response = await fetch(`/api/v1/admin/workflow-config/workflow-templates/${workflowId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const workflow = await response.json();
        
        // Calcola SLA totale sommando tutti i task di tutte le milestone
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
        
        setCalculatedSLA(totalHours > 0 ? totalHours : null);
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
        loadArticoli(),
        loadWorkflows()
      ]);
    } finally {
      setLoading(false);
    }
  };

  // === CRUD FUNCTIONS ===
  const handleEdit = (model: any) => {
    setEditingModel(model);
    setFormData({
      nome: model.nome,
      descrizione: model.descrizione || "",
      articolo_id: model.articolo_id?.toString() || "",
      workflow_template_id: model.workflow_template_id?.toString() || "",
      priority: model.priority || "medium"
    });
    setShowEditForm(true);
  };

  const handleClone = async (model: any) => {
    const newName = prompt(`Clona modello "${model.nome}\n\nInserisci nuovo nome:`, `${model.nome} - Copia`);
    if (!newName) return;
    
    try {
      const response = await fetch(`/api/v1/templates/ticket-templates/${model.id}/clone?new_name=${encodeURIComponent(newName)}`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        }
      });

      if (response.ok) {
        alert("Modello clonato con successo!");
        loadModelli();
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail || "Impossibile clonare modello"}`);
      }
    } catch (error) {
      console.error("Errore clonazione:", error);
      alert("Errore di connessione");
    }
  };

  const handleDelete = async (model: any) => {

  // Funzione wrapper per submit
  const handleFormSubmit = async (e: React.FormEvent) => {
    if (editingModel) {
      await handleSaveEdit(e);
    } else {
      await handleSubmit(e);
    }
  };
    if (!confirm(`Sei sicuro di voler disattivare "${model.nome}"?`)) return;
    
    try {
      const response = await fetch(`/api/v1/templates/ticket-templates/${model.id}`, {
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
        alert(`Errore: ${error.detail || "Impossibile disattivare modello"}`);
      }
    } catch (error) {
      console.error("Errore disattivazione:", error);
      alert("Errore di connessione");
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

  const loadArticoli = async () => {
    try {
      const response = await fetch('/api/v1/admin/workflow-config/articoli', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setArticoli(data);
      }
    } catch (error) {
      console.error('Errore caricamento articoli:', error);
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
        articolo_id: formData.articolo_id ? parseInt(formData.articolo_id) : null,
        workflow_template_id: formData.workflow_template_id ? parseInt(formData.workflow_template_id) : null,
        priority: formData.priority,
        sla_hours: calculatedSLA || 24, // SLA calcolato automaticamente
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
          articolo_id: '',
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

  const getArticoloNome = (id: number | null) => {
    if (!id) return 'Generico';
    const articolo = articoli.find(a => a.id === id);
    return articolo ? `${articolo.codice} - ${articolo.nome}` : 'N/A';
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingModel) return;
    try {
      const payload = {
        nome: formData.nome,
        descrizione: formData.descrizione,
        articolo_id: formData.articolo_id ? parseInt(formData.articolo_id) : null,
        workflow_template_id: formData.workflow_template_id ? parseInt(formData.workflow_template_id) : null,
        priority: formData.priority,
        sla_hours: calculatedSLA || 24,
        is_active: true
      };
      const response = await fetch(`/api/v1/templates/ticket-templates/${editingModel.id}`, {
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
      if (response.ok) {
        alert("Modello aggiornato!");
        setShowEditForm(false);
        setEditingModel(null);
        setFormData({ nome: "", descrizione: "", articolo_id: "", workflow_template_id: "", priority: "medium" });
        setCalculatedSLA(null);
        loadModelli();
      }
    } catch (error) {
      alert("Errore aggiornamento");
    }
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    if (editingModel) {
      await handleSaveEdit(e);
    } else {
      await handleSubmit(e);
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

      {(showForm || showEditForm) && (
        <div style={{
          background: '#f9f9f9',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #ddd'
        }}>
          <h3>{editingModel ? "Modifica Modello Ticket" : "Nuovo Modello Ticket"}</h3>
          <form onSubmit={handleFormSubmit}>
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

              <div>
                <label>Articolo/Servizio</label>
                <select
                  value={formData.articolo_id}
                  onChange={(e) => setFormData({...formData, articolo_id: e.target.value})}
                  style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                >
                  <option value="">Generico (tutti i servizi)</option>
                  {articoli.map(articolo => (
                    <option key={articolo.id} value={articolo.id}>
                      {articolo.codice} - {articolo.nome}
                    </option>
                  ))}
                </select>
              </div>

              <div>
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
              </div>
            </div>

            {/* Visualizzazione SLA calcolato */}
            {calculatedSLA !== null && (
              <div style={{ 
                marginTop: '15px', 
                padding: '10px', 
                background: '#e8f5e8', 
                borderRadius: '4px',
                border: '1px solid #4CAF50'
              }}>
                <strong>SLA Calcolato:</strong> {calculatedSLA} ore 
                <small style={{ marginLeft: '10px', color: '#666' }}>
                  (calcolato automaticamente dalla somma dei task del workflow)
                </small>
              </div>
            )}

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
                  <div><strong>Articolo:</strong> {getArticoloNome(modello.articolo_id)}</div>
                  <div><strong>Workflow:</strong> {getWorkflowNome(modello.workflow_template_id)}</div>
                  <div><strong>Priorità:</strong> {modello.priority}</div>
                  <div><strong>SLA:</strong> {modello.sla_hours} ore</div>
                  <div><strong>Stato:</strong> {modello.is_active ? 'Attivo' : 'Disattivo'}</div>
                  
                  {/* Pulsanti di azione */}
                  <div style={{ 
                    display: "flex", 
                    gap: "8px", 
                    marginTop: "15px",
                    flexWrap: "wrap"
                  }}>
                    <button
                      onClick={() => handleEdit(modello)}
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
                      onClick={() => handleClone(modello)}
                      style={{
                        background: "#FF9800",
                        color: "white",
                        border: "none",
                        padding: "6px 12px",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "12px"
                      }}
                    >
                      📋 Clona
                    </button>
                    
                    <button
                      onClick={() => handleDelete(modello)}
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
                  </div>
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
