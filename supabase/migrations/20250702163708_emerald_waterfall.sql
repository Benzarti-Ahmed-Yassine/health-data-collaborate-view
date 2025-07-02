/*
  # Ajouter support pour spécialités multiples

  1. Nouvelles Tables
    - `patient_specialites` - table de liaison many-to-many
      - `id` (uuid, primary key)
      - `patient_id` (uuid, foreign key vers patients)
      - `specialite_id` (uuid, foreign key vers specialites)
      - `created_at` (timestamp)

  2. Modifications
    - Garder la colonne `specialite` dans patients pour compatibilité
    - Ajouter contrainte unique sur (patient_id, specialite_id)

  3. Sécurité
    - Enable RLS sur patient_specialites
    - Ajouter policies pour accès public
*/

-- Créer table de liaison patient-spécialités
CREATE TABLE IF NOT EXISTS patient_specialites (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id uuid NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  specialite_id uuid NOT NULL REFERENCES specialites(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  UNIQUE(patient_id, specialite_id)
);

-- Enable Row Level Security
ALTER TABLE patient_specialites ENABLE ROW LEVEL SECURITY;

-- Créer policies pour patient_specialites
CREATE POLICY "Allow all operations on patient_specialites"
  ON patient_specialites
  FOR ALL
  TO public
  USING (true)
  WITH CHECK (true);

-- Ajouter policy pour supprimer des spécialités
CREATE POLICY "Allow delete access to specialites"
  ON specialites
  FOR DELETE
  TO public
  USING (true);