// Types for our database tables
export interface Patient {
  id: string
  prenom: string
  nom: string
  age: number
  glycemie: string
  ta: string
  taille: number
  poids: number
  imc: number
  specialite: string
  medicaments: string
  notes: string
  created_at: string
  updated_at: string
  specialites?: Specialite[]
}

export interface Specialite {
  id: string
  nom: string
  created_at: string
}

export interface PatientSpecialite {
  id: string
  patient_id: string
  specialite_id: string
  created_at: string
  specialite?: Specialite
}

export interface FamilleMedicament {
  id: string
  nom: string
  description: string
  created_at: string
  medicaments?: Medicament[]
}

export interface Medicament {
  id: string
  nom: string
  famille_id: string
  dosage: string
  forme: string
  stock_actuel: number
  stock_minimum: number
  prix_unitaire: number
  description: string
  created_at: string
  updated_at: string
  famille?: FamilleMedicament
}
