/*
  # Create patient management system tables

  1. New Tables
    - `specialites`
      - `id` (uuid, primary key)
      - `nom` (text, unique, not null)
      - `created_at` (timestamp)
    - `patients`
      - `id` (uuid, primary key)
      - `prenom` (text, not null)
      - `nom` (text, not null)
      - `age` (integer, not null)
      - `glycemie` (text)
      - `ta` (text)
      - `taille` (numeric)
      - `poids` (numeric)
      - `imc` (numeric)
      - `specialite` (text)
      - `medicaments` (text)
      - `notes` (text)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    - `patient_specialites`
      - `id` (uuid, primary key)
      - `patient_id` (uuid, foreign key)
      - `specialite_id` (uuid, foreign key)
      - `created_at` (timestamp)
      - Unique constraint on (patient_id, specialite_id)

  2. Security
    - Enable RLS on all tables
    - Add policies for public access (adjust as needed)

  3. Functions
    - Add trigger function for updating updated_at column
    - Add trigger on patients table for auto-updating updated_at
</sql>

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create specialites table
CREATE TABLE IF NOT EXISTS specialites (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  nom text UNIQUE NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Create patient_specialites junction table
CREATE TABLE IF NOT EXISTS patient_specialites (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  patient_id uuid NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  specialite_id uuid NOT NULL REFERENCES specialites(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  UNIQUE(patient_id, specialite_id)
);

-- Add trigger for updating updated_at on patients table
CREATE TRIGGER update_patients_updated_at
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE specialites ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE patient_specialites ENABLE ROW LEVEL SECURITY;

-- Create policies for specialites
CREATE POLICY "Allow read access to specialites" ON specialites FOR SELECT USING (true);
CREATE POLICY "Allow insert access to specialites" ON specialites FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow delete access to specialites" ON specialites FOR DELETE USING (true);

-- Create policies for patients
CREATE POLICY "Allow all operations on patients" ON patients FOR ALL USING (true) WITH CHECK (true);

-- Create policies for patient_specialites
CREATE POLICY "Allow all operations on patient_specialites" ON patient_specialites FOR ALL USING (true) WITH CHECK (true);