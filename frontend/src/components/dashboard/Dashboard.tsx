import React from 'react';
import styles from '../../styles/common.module.css';

const Dashboard: React.FC = () => {
  return (
    <div className={styles.container}>
      <h1 className={styles.pageTitle}>
        📊 Dashboard
      </h1>
      
      <div className={styles.statsGrid}>
        <div className={`${styles.statCard} ${styles.statCardBlue}`}>
          <div className={styles.statValue}>15</div>
          <div className={styles.statLabel}>Utenti Totali</div>
        </div>

        <div className={`${styles.statCard} ${styles.statCardGreen}`}>
          <div className={styles.statValue}>1,227</div>
          <div className={styles.statLabel}>Aziende</div>
        </div>

        <div className={`${styles.statCard} ${styles.statCardPurple}`}>
          <div className={styles.statValue}>32</div>
          <div className={styles.statLabel}>Documenti RAG</div>
        </div>

        <div className={`${styles.statCard} ${styles.statCardOrange}`}>
          <div className={styles.statValue}>✅</div>
          <div className={styles.statLabel}>Sistema Operativo</div>
        </div>
      </div>

      <div className={styles.card}>
        <h2 className={styles.cardHeader}>
          🚀 IntelligenceHUB v5.0
        </h2>
        <p className={styles.textMuted}>
          Sistema di intelligenza artificiale completamente operativo con integrazione CRM, 
          gestione documenti RAG, assessment digitale e automazioni intelligenti.
        </p>
        <div className={styles.mt4}>
          <span className={`${styles.badge} ${styles.badgeSuccess}`}>
            ✅ Sistema Operativo al 100%
          </span>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
