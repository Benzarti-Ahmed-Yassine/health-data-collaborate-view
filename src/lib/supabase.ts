import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

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
}

export interface Specialite {
  id: string
  nom: string
  created_at: string
}