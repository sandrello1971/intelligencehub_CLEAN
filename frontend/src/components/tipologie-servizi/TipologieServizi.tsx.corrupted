import React, { useState, useEffect } from 'react';
import './TipologieServizi.css';

interface TipologiaServizio {
  id: number;
  nome: string;
  descrizione: string;
  colore: string;
  icona: string;
  attivo: boolean;
  created_at: string;
}

interface TipologiaFormData {
  nome: string;
  descrizione: string;
  colore: string;
  icona: string;
  attivo: boolean;
}

const TipologieServizi: React.FC = () => {
  const [tipologie, setTipologie] = useState<TipologiaServizio[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTipologia, setEditingTipologia] = useState<TipologiaServizio | null>(null);
  const [formData, setFormData] = useState<TipologiaFormData>({
    nome: '',
    descrizione: '',
    colore: '#3B82F6',
    icona: '📋',
    attivo: true
  });

  // Icone predefinite
  const iconeDisponibili = [
    '💰', '💻', '📊', '🎓', '📢', '⚖️', '🔧', '🎯', '📈', '🌟',
    '🏆', '🚀', '💡', '🔥', '⭐', '📱', '🎨', '🔒', '🌐', '📋'
  ];

  // Colori predefiniti
  const coloriDisponibili = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#6B7280',
    '#EC4899', '#14B8A6', '#F97316', '#84CC16', '#06B6D4', '#8B5A2B'
  ];

  // Fetch tipologie
  const fetchTipologie = async (search = '') => {
    try {
      const searchParam = search ? `?search=${encodeURIComponent(search)}` : '';
      const response = await fetch(`/api/v1/tipologie-servizi/${searchParam}`);
      const data = await response.json();
      
      if (data.success) {
        setTipologie(data.tipologie);
      }
    } catch (error) {
      console.error('Error fetching tipologie:', error);
    } finally {
      setLoading(false);
    }
  };

  // Create tipologia
  const createTipologia = async () => {

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
    try {

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      const response = await fetch('/api/v1/tipologie-servizi/', {

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
        method: 'POST',

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
        headers: { 'Content-Type': 'application/json' },

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
        body: JSON.stringify(formData)

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      });

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      const data = await response.json();

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      if (data.success) {

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
        setShowCreateModal(false);

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
        setFormData({

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
          nome: '',

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
          descrizione: '',

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
          colore: '#3B82F6',

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
          icona: '📋',

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
          attivo: true

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
        });

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
        fetchTipologie(searchTerm);

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
        alert(`✅ ${data.message}`);

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      } else {

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
        alert(`❌ Errore: ${data.error || 'Creazione fallita'}`);

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      }

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
    } catch (error) {

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      console.error('Error creating tipologia:', error);

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
      alert('❌ Errore durante la creazione');

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
    }

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };
  };

  // Open edit modal
  const openEditModal = (tipologia: TipologiaServizio) => {
    setEditingTipologia(tipologia);
    setFormData({
      nome: tipologia.nome,
      descrizione: tipologia.descrizione || "",
      colore: tipologia.colore || "#3B82F6",
      icona: tipologia.icona || "📋",
      attivo: tipologia.attivo
    });
    setShowEditModal(true);
  };

  // Update tipologia
  const updateTipologia = async () => {
    if (!editingTipologia) return;
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${editingTipologia.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setShowEditModal(false);
        setEditingTipologia(null);
        fetchTipologie();
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.detail || "Aggiornamento fallito"}`);
      }
    } catch (error) {
      console.error("Error updating tipologia:", error);
      alert("❌ Errore durante l'aggiornamento");
    }
  };

  // Delete tipologia
  const deleteTipologia = async (tipologia: TipologiaServizio) => {
    if (!window.confirm(`Sei sicuro di voler eliminare la tipologia "${tipologia.nome}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`/api/v1/tipologie-servizi/${tipologia.id}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchTipologie(searchTerm);
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ Errore: ${data.error || 'Eliminazione fallita'}`);
      }
    } catch (error) {
      console.error('Error deleting tipologia:', error);
      alert('❌ Errore durante l\'eliminazione');
    }
  };

  // Effects
  useEffect(() => {
    fetchTipologie();
  }, []);

  if (loading) {
    return (
      <div className="tipologie-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          Caricamento tipologie...
        </div>
      </div>
    );
  }

  return (
    <div className="tipologie-container">
      <div className="tipologie-header">
        <div className="tipologie-title">
          <h1>🏷️ Tipologie Servizi</h1>
          <p>Gestisci le categorie dei tuoi servizi</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          ➕ Nuova Tipologia
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{tipologie.length}</div>
          <div className="stat-label">Totali</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{tipologie.filter(t => t.attivo).length}</div>
          <div className="stat-label">Attive</div>
        </div>
      </div>

      <div className="tipologie-grid">
        {tipologie.map((tipologia) => (
          <div key={tipologia.id} className="tipologia-card">
            <div className="tipologia-card-header">
              <div className="tipologia-preview">
                <span 
                  className="tipologia-icon"
                  style={{ backgroundColor: tipologia.colore + '20', color: tipologia.colore }}
                >
                  {tipologia.icona}
                </span>
                <div className="tipologia-info">
                  <h3>{tipologia.nome}</h3>
                  <span className={`status-badge ${tipologia.attivo ? 'active' : 'inactive'}`}>
                    {tipologia.attivo ? '✅ Attiva' : '❌ Inattiva'}
                  </span>
                </div>
              </div>
              <div className="tipologia-actions">
                <button
                <button
                  className="btn btn-edit btn-sm"
                  onClick={() => openEditModal(tipologia)}
                  title="Modifica"
                >
                  ✏️
                </button>
                  className="btn btn-danger btn-sm"
                  onClick={() => deleteTipologia(tipologia)}
                  title="Elimina"
                >
                  🗑️
                </button>
              </div>
            </div>
            {tipologia.descrizione && (
              <div className="tipologia-description">
                {tipologia.descrizione}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Create Modal - Versione semplificata */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>➕ Nuova Tipologia</h2>
              <button onClick={() => setShowCreateModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                  placeholder="Es: Servizi Digitali"
                />
              </div>
              <div className="form-group">
                <label>Descrizione</label>
                <textarea
                  value={formData.descrizione}
                  onChange={(e) => setFormData({...formData, descrizione: e.target.value})}
                  placeholder="Descrizione tipologia"
                  rows={3}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Icona</label>
                  <select
                    value={formData.icona}
                    onChange={(e) => setFormData({...formData, icona: e.target.value})}
                  >
                    {iconeDisponibili.map(icona => (
                      <option key={icona} value={icona}>{icona} {icona}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Colore</label>
                  <select
                    value={formData.colore}
                    onChange={(e) => setFormData({...formData, colore: e.target.value})}
                  >
                    {coloriDisponibili.map(colore => (
                      <option key={colore} value={colore}>{colore}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                Annulla
              </button>
              <button 
                className="btn btn-primary"
                onClick={createTipologia}
                disabled={!formData.nome}
              >
                Crea
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TipologieServizi;
