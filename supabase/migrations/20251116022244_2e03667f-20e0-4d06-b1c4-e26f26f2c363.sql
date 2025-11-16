-- Create specialites table
CREATE TABLE IF NOT EXISTS public.specialites (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  nom TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create patients table  
CREATE TABLE IF NOT EXISTS public.patients (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  prenom TEXT NOT NULL,
  nom TEXT NOT NULL,
  age INTEGER NOT NULL,
  glycemie TEXT,
  ta TEXT,
  taille NUMERIC DEFAULT 0,
  poids NUMERIC DEFAULT 0,
  imc NUMERIC DEFAULT 0,
  specialite TEXT,
  medicaments TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create patient_specialites junction table
CREATE TABLE IF NOT EXISTS public.patient_specialites (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  patient_id UUID NOT NULL REFERENCES public.patients(id) ON DELETE CASCADE,
  specialite_id UUID NOT NULL REFERENCES public.specialites(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(patient_id, specialite_id)
);

-- Create famille_medicaments table
CREATE TABLE IF NOT EXISTS public.famille_medicaments (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  nom TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create medicaments table
CREATE TABLE IF NOT EXISTS public.medicaments (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  nom TEXT NOT NULL,
  famille_id UUID NOT NULL REFERENCES public.famille_medicaments(id) ON DELETE RESTRICT,
  dosage TEXT NOT NULL,
  forme TEXT NOT NULL,
  stock_actuel INTEGER NOT NULL DEFAULT 0,
  stock_minimum INTEGER NOT NULL DEFAULT 10,
  prix_unitaire NUMERIC NOT NULL DEFAULT 0,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS on all tables
ALTER TABLE public.specialites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patient_specialites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.famille_medicaments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.medicaments ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allowing all operations for now - you can restrict based on your needs)
CREATE POLICY "Allow all operations on specialites" ON public.specialites FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on patients" ON public.patients FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on patient_specialites" ON public.patient_specialites FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on famille_medicaments" ON public.famille_medicaments FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on medicaments" ON public.medicaments FOR ALL USING (true) WITH CHECK (true);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_patients_updated_at
  BEFORE UPDATE ON public.patients
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_medicaments_updated_at
  BEFORE UPDATE ON public.medicaments
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Enable realtime for all tables
ALTER PUBLICATION supabase_realtime ADD TABLE public.specialites;
ALTER PUBLICATION supabase_realtime ADD TABLE public.patients;
ALTER PUBLICATION supabase_realtime ADD TABLE public.patient_specialites;
ALTER PUBLICATION supabase_realtime ADD TABLE public.famille_medicaments;
ALTER PUBLICATION supabase_realtime ADD TABLE public.medicaments;