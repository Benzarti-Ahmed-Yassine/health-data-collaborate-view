/*
  # Création des tables pour la gestion de pharmacie

  1. Nouvelles Tables
    - `famille_medicaments`
      - `id` (uuid, primary key)
      - `nom` (text, unique) - nom de la famille (ex: Antibiotiques, Antalgiques)
      - `description` (text) - description de la famille
      - `created_at` (timestamp)
    
    - `medicaments`
      - `id` (uuid, primary key)
      - `nom` (text, unique) - nom du médicament
      - `famille_id` (uuid, foreign key) - référence à la famille
      - `dosage` (text) - dosage du médicament
      - `forme` (text) - forme galénique (comprimé, sirop, etc.)
      - `stock_actuel` (integer) - quantité en stock
      - `stock_minimum` (integer) - seuil d'alerte
      - `prix_unitaire` (numeric) - prix par unité
      - `description` (text) - description/indications
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Sécurité
    - Enable RLS sur toutes les tables
    - Politiques permissives pour le développement

  3. Fonctionnalités
    - Trigger pour mise à jour automatique des timestamps
    - Contraintes d'intégrité
    - Index pour les performances
*/

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Table des familles de médicaments
CREATE TABLE IF NOT EXISTS famille_medicaments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nom text UNIQUE NOT NULL,
  description text DEFAULT '',
  created_at timestamptz DEFAULT now()
);

-- Table des médicaments
CREATE TABLE IF NOT EXISTS medicaments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nom text UNIQUE NOT NULL,
  famille_id uuid NOT NULL REFERENCES famille_medicaments(id) ON DELETE CASCADE,
  dosage text DEFAULT '',
  forme text DEFAULT '',
  stock_actuel integer DEFAULT 0,
  stock_minimum integer DEFAULT 10,
  prix_unitaire numeric DEFAULT 0,
  description text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_medicaments_famille_id ON medicaments(famille_id);
CREATE INDEX IF NOT EXISTS idx_medicaments_stock ON medicaments(stock_actuel);
CREATE INDEX IF NOT EXISTS idx_medicaments_nom ON medicaments(nom);

-- Trigger pour updated_at sur medicaments
DROP TRIGGER IF EXISTS update_medicaments_updated_at ON medicaments;
CREATE TRIGGER update_medicaments_updated_at
    BEFORE UPDATE ON medicaments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE famille_medicaments ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicaments ENABLE ROW LEVEL SECURITY;

-- Politiques RLS permissives pour le développement
CREATE POLICY "Allow all operations on famille_medicaments"
  ON famille_medicaments
  FOR ALL
  TO public
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow all operations on medicaments"
  ON medicaments
  FOR ALL
  TO public
  USING (true)
  WITH CHECK (true);

-- Insertion de données de test pour les familles de médicaments
INSERT INTO famille_medicaments (nom, description) VALUES
  ('Antalgiques', 'Médicaments contre la douleur'),
  ('Antibiotiques', 'Médicaments contre les infections bactériennes'),
  ('Anti-inflammatoires', 'Médicaments contre l''inflammation'),
  ('Antihypertenseurs', 'Médicaments contre l''hypertension'),
  ('Antidiabétiques', 'Médicaments pour le diabète'),
  ('Vitamines', 'Compléments vitaminiques'),
  ('Antihistaminiques', 'Médicaments contre les allergies'),
  ('Bronchodilatateurs', 'Médicaments pour l''asthme et BPCO')
ON CONFLICT (nom) DO NOTHING;

-- Insertion de quelques médicaments de test
INSERT INTO medicaments (nom, famille_id, dosage, forme, stock_actuel, stock_minimum, prix_unitaire, description)
SELECT 
  'Paracétamol',
  f.id,
  '500mg',
  'Comprimé',
  100,
  20,
  0.15,
  'Antalgique et antipyrétique'
FROM famille_medicaments f WHERE f.nom = 'Antalgiques'
ON CONFLICT (nom) DO NOTHING;

INSERT INTO medicaments (nom, famille_id, dosage, forme, stock_actuel, stock_minimum, prix_unitaire, description)
SELECT 
  'Amoxicilline',
  f.id,
  '1g',
  'Comprimé',
  50,
  15,
  1.20,
  'Antibiotique à large spectre'
FROM famille_medicaments f WHERE f.nom = 'Antibiotiques'
ON CONFLICT (nom) DO NOTHING;

INSERT INTO medicaments (nom, famille_id, dosage, forme, stock_actuel, stock_minimum, prix_unitaire, description)
SELECT 
  'Ibuprofène',
  f.id,
  '400mg',
  'Comprimé',
  75,
  25,
  0.25,
  'Anti-inflammatoire non stéroïdien'
FROM famille_medicaments f WHERE f.nom = 'Anti-inflammatoires'
ON CONFLICT (nom) DO NOTHING;