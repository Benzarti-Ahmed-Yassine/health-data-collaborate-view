/*
  # Create patients management schema

  1. New Tables
    - `patients`
      - `id` (uuid, primary key)
      - `prenom` (text, first name)
      - `nom` (text, last name)
      - `age` (integer)
      - `glycemie` (text, blood sugar)
      - `ta` (text, blood pressure)
      - `taille` (numeric, height in cm)
      - `poids` (numeric, weight in kg)
      - `imc` (numeric, BMI)
      - `specialite` (text, specialty)
      - `medicaments` (text, medications)
      - `notes` (text, medical notes)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    
    - `specialites`
      - `id` (uuid, primary key)
      - `nom` (text, specialty name)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS on both tables
    - Add policies for public access (since this is a medical management system)
*/

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  prenom text NOT NULL,
  nom text NOT NULL,
  age integer NOT NULL,
  glycemie text DEFAULT '',
  ta text DEFAULT '',
  taille numeric DEFAULT 0,
  poids numeric DEFAULT 0,
  imc numeric DEFAULT 0,
  specialite text DEFAULT '',
  medicaments text DEFAULT '',
  notes text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create specialites table
CREATE TABLE IF NOT EXISTS specialites (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nom text UNIQUE NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Insert default specialties
INSERT INTO specialites (nom) VALUES
  ('Généraliste'),
  ('Pédodontiste'),
  ('Orthophoniste'),
  ('Pédiatre'),
  ('Cancérologue'),
  ('Nutritionniste'),
  ('Gériatre'),
  ('Gastro-entérologue'),
  ('Ergothérapeute'),
  ('Endocrinologue'),
  ('Pneumologue'),
  ('Sage-femme'),
  ('Ophtalmologue'),
  ('Gynécologue'),
  ('Puéricultrice'),
  ('Cardiologue'),
  ('Urologue'),
  ('Dentiste'),
  ('Diabétologue')
ON CONFLICT (nom) DO NOTHING;

-- Enable Row Level Security
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE specialites ENABLE ROW LEVEL SECURITY;

-- Create policies for patients table (public access for medical staff)
CREATE POLICY "Allow all operations on patients"
  ON patients
  FOR ALL
  TO public
  USING (true)
  WITH CHECK (true);

-- Create policies for specialites table
CREATE POLICY "Allow read access to specialites"
  ON specialites
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow insert access to specialites"
  ON specialites
  FOR INSERT
  TO public
  WITH CHECK (true);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for patients table
CREATE TRIGGER update_patients_updated_at
  BEFORE UPDATE ON patients
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();