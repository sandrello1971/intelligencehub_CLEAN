-- Intelligence HUB - Inserimento completo servizi e milestone

-- 1. Inserimento Sub Types (servizi)
INSERT INTO sub_types (name, code) VALUES 
('Cashback', 'CBK'),
('Know How', 'KHW'), 
('Bandi', 'BND'),
('Finanziamenti', 'FNZ'),
('Incarico 24 mesi', 'I24'),
('Patent Box', 'PBX'),
('Collaborazione', 'COL'),
('Formazione 4.0', 'F40'),
('Generico', 'GEN'),
('Transizione 5.0', 'T50'),
('Altro', 'ZZZ')
ON CONFLICT (code) DO NOTHING;

-- 2. Inserimento Milestone per Cashback (2)
INSERT INTO milestones (name, project_type, "order") VALUES
('Incarico Cashback Firmato', 'CBK', 1),
('Cashback Erogato', 'CBK', 2);

-- 3. Inserimento Milestone per Know How (9) 
INSERT INTO milestones (name, project_type, "order") VALUES
('Incarico Enduser Firmato', 'KHW', 1),
('Company Profile Acquisito', 'KHW', 2),
('Progetto Quarenghi Inviato', 'KHW', 3),
('Progetto Quarenghi Firmato', 'KHW', 4),
('Bozza di Relazione Presentata', 'KHW', 5),
('Bozza Uscita', 'KHW', 6),
('Bozza Approvata, Fattura Emessa', 'KHW', 7),
('Pagamento Effettuato', 'KHW', 8),
('Pratica Conclusa', 'KHW', 9);

-- 4. Inserimento Milestone per Bandi (6)
INSERT INTO milestones (name, project_type, "order") VALUES
('Richiesta Inviata a ClickBando', 'BND', 1),
('Inviato Ordine a ClickBando', 'BND', 2),
('Inviata Documentazione a ClickBando', 'BND', 3),
('Incarico 24 mesi Firmato', 'BND', 4),
('Assegnazione Acquisita', 'BND', 5),
('Fattura Emessa', 'BND', 6);

-- 5. Inserimento Milestone per Finanziamenti (2)
INSERT INTO milestones (name, project_type, "order") VALUES
('Incarico Finanziamenti Firmato', 'FNZ', 1),
('Finanziamento Erogato', 'FNZ', 2);

-- 6. Inserimento Milestone per Incarico 24 mesi (3)
INSERT INTO milestones (name, project_type, "order") VALUES
('Predisposizione Incarico', 'I24', 1),
('Invio Incarico', 'I24', 2),
('Firma Incarico Completata', 'I24', 3);

-- 7. Inserimento Milestone per Patent Box (9)
INSERT INTO milestones (name, project_type, "order") VALUES
('Incarico Enduser Firmato', 'PBX', 1),
('Company Profile Acquisito', 'PBX', 2), 
('Progetto Quarenghi Inviato', 'PBX', 3),
('Progetto Quarenghi Firmato', 'PBX', 4),
('Bozza di Relazione Presentata', 'PBX', 5),
('Bozza Uscita', 'PBX', 6),
('Bozza Approvata, Fattura Emessa', 'PBX', 7),
('Pagamento Effettuato', 'PBX', 8),
('Pratica Conclusa', 'PBX', 9);

-- 8. Inserimento Milestone per Collaborazione (2)
INSERT INTO milestones (name, project_type, "order") VALUES
('Prospettiva di Collaborazione', 'COL', 1),
('Incarico EndUser Firmato', 'COL', 2);

-- 9. Inserimento Milestone per Formazione 4.0 (9)
INSERT INTO milestones (name, project_type, "order") VALUES
('Firma Incarico EU', 'F40', 1),
('Firma Progetto Quarenghi', 'F40', 2),
('Pratica in Revisione', 'F40', 3),
('Pratica Terminata', 'F40', 4),
('Bozza di Relazione Presentata', 'F40', 5),
('Bozza Approvata - Revisione in Corso', 'F40', 6),
('Revisione Conclusa', 'F40', 7),
('Fatture Pagate', 'F40', 8),
('Pratica Conclusa', 'F40', 9);

-- 10. Inserimento Milestone per Generico (1)
INSERT INTO milestones (name, project_type, "order") VALUES
('Contatto Iniziale', 'GEN', 1);

-- 11. Inserimento Milestone per Transizione 5.0 (8)
INSERT INTO milestones (name, project_type, "order") VALUES
('Incarico 24 mesi Firmato', 'T50', 1),
('Fattibilità Verificata', 'T50', 2),
('Ex-Ante Conclusa', 'T50', 3),
('Ordini e Pagamenti Effettuati', 'T50', 4),
('Ex-Post Conclusa', 'T50', 5),
('Credito Confermato', 'T50', 6),
('Credito Erogato', 'T50', 7),
('Fattura Emessa', 'T50', 8);

-- 12. Inserimento Milestone per Altro (1)
INSERT INTO milestones (name, project_type, "order") VALUES
('Persa', 'ZZZ', 1);
