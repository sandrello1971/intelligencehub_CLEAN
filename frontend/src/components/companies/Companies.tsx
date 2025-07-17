import React, { useState, useEffect } from 'react';
import CompanyEditModal from './CompanyEditModal';
import CompanyEditModal from './CompanyEditModal';
import styles from '../../styles/common.module.css';

interface Company {
  id: number;
  name: string;
  settore?: string;
  partita_iva?: string;
  email?: string;
  telefono?: string;
  sito_web?: string;
  citta?: string;
  provincia?: string;
  is_partner: boolean;
  is_supplier: boolean;
  partner_category?: string;
  partner_rating: number;
  numero_dipendenti?: number;
  scraping_status: string;
  created_at: string;
}

interface CompaniesStats {
  total_companies: number;
  partners_count: number;
  suppliers_count: number;
  scraped_count: number;
  avg_partner_rating: number;
  sectors_count: number;
}

const Companies: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [stats, setStats] = useState<CompaniesStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPartner, setFilterPartner] = useState<string>('all');
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [editingCompany, setEditingCompany] = useState<Company | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCompanies, setTotalCompanies] = useState(0);
  
  const companiesPerPage = 20;

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const offset = (currentPage - 1) * companiesPerPage;
      let url = `/api/v1/companies/?limit=${companiesPerPage}&offset=${offset}`;
      
      if (searchTerm) {
        url += `&search=${encodeURIComponent(searchTerm)}`;
      }
      
      if (filterPartner !== 'all') {
        url += `&is_partner=${filterPartner === 'partner'}`;
      }
      
      const response = await fetch(url);
      const data = await response.json();
      
      setCompanies(data.companies || []);
      setTotalCompanies(data.total || 0);
    } catch (error) {
      console.error('Error fetching companies:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/v1/companies/stats/overview');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, [currentPage, searchTerm, filterPartner]);

  useEffect(() => {
    fetchStats();
  }, []);

  const totalPages = Math.ceil(totalCompanies / companiesPerPage);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchCompanies();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT');
  };

  const getPartnerBadge = (company: Company) => {
    if (company.is_partner) {
      return <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">Partner</span>;
    }
    if (company.is_supplier) {
      return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">Supplier</span>;
    }
    return <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">Cliente</span>;
  };

  return (
    <div className={styles.container}>
      <div className="flex justify-between items-center mb-6">
        <h1 className={styles.pageTitle}>🏢 Aziende</h1>
        <div className="text-sm text-gray-500">
          {totalCompanies.toLocaleString()} aziende totali
        </div>
      </div>

      {stats && (
        <div className={styles.statsGrid} style={{ marginBottom: '2rem' }}>
          <div className={`${styles.statCard} ${styles.statCardBlue}`}>
            <div className={styles.statValue}>{stats.total_companies.toLocaleString()}</div>
            <div className={styles.statLabel}>Aziende Totali</div>
          </div>
          <div className={`${styles.statCard} ${styles.statCardGreen}`}>
            <div className={styles.statValue}>{stats.partners_count}</div>
            <div className={styles.statLabel}>Partner</div>
          </div>
          <div className={`${styles.statCard} ${styles.statCardPurple}`}>
            <div className={styles.statValue}>{stats.suppliers_count}</div>
            <div className={styles.statLabel}>Supplier</div>
          </div>
          <div className={`${styles.statCard} ${styles.statCardOrange}`}>
            <div className={styles.statValue}>{stats.sectors_count}</div>
            <div className={styles.statLabel}>Settori</div>
          </div>
        </div>
      )}

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
        <form onSubmit={handleSearch} className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cerca aziende
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Nome azienda o settore..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo
            </label>
            <select
              value={filterPartner}
              onChange={(e) => setFilterPartner(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">Tutti</option>
              <option value="partner">Solo Partner</option>
              <option value="client">Solo Clienti</option>
            </select>
          </div>
          
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500"
          >
            🔍 Cerca
          </button>
        </form>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Lista Aziende ({totalCompanies.toLocaleString()})
          </h3>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Caricamento aziende...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Azienda
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Settore
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Località
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dipendenti
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Azioni
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {companies.map((company) => (
                  <tr key={company.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {company.name?.replace(/'/g, '') || 'N/A'}
                        </div>
                        {company.partita_iva && (
                          <div className="text-sm text-gray-500">
                            P.IVA: {company.partita_iva}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {company.settore || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {company.citta ? `${company.citta} (${company.provincia})` : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getPartnerBadge(company)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {company.numero_dipendenti || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => setEditingCompany(company)}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        ✏️ Modifica
                      </button>
                      {company.sito_web && (
                        <a
                          href={company.sito_web.startsWith('http') ? company.sito_web : `https://${company.sito_web}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-green-600 hover:text-green-900"
                        >
                          🌐 Sito
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
            <div className="text-sm text-gray-700">
              Pagina {currentPage} di {totalPages}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                ← Precedente
              </button>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Successiva →
              </button>
            </div>
          </div>
        )}
      </div>

      {editingCompany && (
        <CompanyEditModal
          company={editingCompany}
          onClose={() => setEditingCompany(null)}
          onSave={(updatedCompany) => {
            // Aggiorna la lista companies
            setCompanies(companies.map(c => c.id === updatedCompany.id ? updatedCompany : c));
            setEditingCompany(null);
            // Refresh stats
            fetchStats();
          }}
        />
      )}

      
      {selectedCompany && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto mx-4">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                {selectedCompany.name?.replace(/'/g, '')}
              </h2>
              <button
                onClick={() => setSelectedCompany(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <strong>Settore:</strong> {selectedCompany.settore || 'N/A'}
              </div>
              <div>
                <strong>P.IVA:</strong> {selectedCompany.partita_iva || 'N/A'}
              </div>
              <div>
                <strong>Email:</strong> {selectedCompany.email || 'N/A'}
              </div>
              <div>
                <strong>Telefono:</strong> {selectedCompany.telefono || 'N/A'}
              </div>
              <div>
                <strong>Città:</strong> {selectedCompany.citta || 'N/A'}
              </div>
              <div>
                <strong>Provincia:</strong> {selectedCompany.provincia || 'N/A'}
              </div>
              <div>
                <strong>Dipendenti:</strong> {selectedCompany.numero_dipendenti || 'N/A'}
              </div>
              <div>
                <strong>Tipo:</strong> {getPartnerBadge(selectedCompany)}
              </div>
              {selectedCompany.sito_web && (
                <div className="col-span-2">
                  <strong>Sito Web:</strong>{' '}
                  <a
                    href={selectedCompany.sito_web.startsWith('http') ? selectedCompany.sito_web : `https://${selectedCompany.sito_web}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline ml-2"
                  >
                    {selectedCompany.sito_web}
                  </a>
                </div>
              )}
              <div className="col-span-2">
                <strong>Aggiunta il:</strong> {formatDate(selectedCompany.created_at)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Companies;
