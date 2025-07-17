# Trova la riga con "success": false e aggiungere logica per duplicati
sed -i '/if (response.ok) {/,/} else {/c\
      if (response.ok) {\
        const result = await response.json();\
        if (result.success || result.message.includes("duplicate key")) {\
          setScrapingStatus("✅ Scraping completato (o già esistente)!");\
          setFormData(prev => ({\
            ...prev,\
            scraping_status: "completed"\
          }));\
        } else {\
          setScrapingStatus(`❌ Errore: ${result.message}`);\
        }\
      } else {' src/components/companies/CompanyEditModal.tsx
