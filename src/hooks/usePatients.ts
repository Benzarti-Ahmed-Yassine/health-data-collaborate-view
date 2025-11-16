import { useState, useEffect } from 'react'
import { supabase } from '@/integrations/supabase/client'
import type { Patient, Specialite } from '@/types/database'
import { useToast } from '@/hooks/use-toast'

export const usePatients = () => {
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  const fetchPatients = async () => {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('patients')
        .select(`
          *,
          patient_specialites (
            id,
            specialite_id,
            specialites (
              id,
              nom,
              created_at
            )
          )
        `)
        .order('created_at', { ascending: false })

      if (error) throw error
      
      // Transformer les données pour inclure les spécialités
      const patientsWithSpecialites = data?.map(patient => ({
        ...patient,
        specialites: patient.patient_specialites?.map(ps => ps.specialites).filter(Boolean) || []
      })) || []
      
      setPatients(patientsWithSpecialites)
    } catch (error) {
      console.error('Error fetching patients:', error)
      toast({
        title: "Erreur",
        description: "Impossible de charger les patients",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const addPatient = async (patientData: Omit<Patient, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const { data, error } = await supabase
        .from('patients')
        .insert([patientData])
        .select()
        .single()

      if (error) throw error
      
      await fetchPatients() // Recharger pour avoir les spécialités
      toast({
        title: "Patient ajouté",
        description: `${data.prenom} ${data.nom} a été ajouté avec succès.`
      })
      return data
    } catch (error) {
      console.error('Error adding patient:', error)
      toast({
        title: "Erreur",
        description: "Impossible d'ajouter le patient",
        variant: "destructive"
      })
      throw error
    }
  }

  const updatePatient = async (id: string, patientData: Partial<Patient>) => {
    try {
      const { data, error } = await supabase
        .from('patients')
        .update(patientData)
        .eq('id', id)
        .select()
        .single()

      if (error) throw error

      await fetchPatients() // Recharger pour avoir les spécialités
      toast({
        title: "Patient modifié",
        description: `${data.prenom} ${data.nom} a été modifié avec succès.`
      })
      return data
    } catch (error) {
      console.error('Error updating patient:', error)
      toast({
        title: "Erreur",
        description: "Impossible de modifier le patient",
        variant: "destructive"
      })
      throw error
    }
  }

  const deletePatient = async (id: string) => {
    try {
      const { error } = await supabase
        .from('patients')
        .delete()
        .eq('id', id)

      if (error) throw error

      setPatients(prev => prev.filter(p => p.id !== id))
      toast({
        title: "Patient supprimé",
        description: "Le patient a été supprimé avec succès."
      })
    } catch (error) {
      console.error('Error deleting patient:', error)
      toast({
        title: "Erreur",
        description: "Impossible de supprimer le patient",
        variant: "destructive"
      })
      throw error
    }
  }

  const addSpecialiteToPatient = async (patientId: string, specialiteId: string) => {
    try {
      const { error } = await supabase
        .from('patient_specialites')
        .insert([{ patient_id: patientId, specialite_id: specialiteId }])

      if (error) throw error

      await fetchPatients()
      toast({
        title: "Spécialité ajoutée",
        description: "La spécialité a été ajoutée au patient avec succès."
      })
    } catch (error) {
      console.error('Error adding specialite to patient:', error)
      toast({
        title: "Erreur",
        description: "Impossible d'ajouter la spécialité au patient",
        variant: "destructive"
      })
      throw error
    }
  }

  const removeSpecialiteFromPatient = async (patientId: string, specialiteId: string) => {
    try {
      const { error } = await supabase
        .from('patient_specialites')
        .delete()
        .eq('patient_id', patientId)
        .eq('specialite_id', specialiteId)

      if (error) throw error

      await fetchPatients()
      toast({
        title: "Spécialité supprimée",
        description: "La spécialité a été supprimée du patient avec succès."
      })
    } catch (error) {
      console.error('Error removing specialite from patient:', error)
      toast({
        title: "Erreur",
        description: "Impossible de supprimer la spécialité du patient",
        variant: "destructive"
      })
      throw error
    }
  }

  useEffect(() => {
    fetchPatients()

    // Set up real-time subscription
    const subscription = supabase
      .channel('patients_changes')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'patients' },
        () => fetchPatients()
      )
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'patient_specialites' },
        () => fetchPatients()
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  return {
    patients,
    loading,
    addPatient,
    updatePatient,
    deletePatient,
    addSpecialiteToPatient,
    removeSpecialiteFromPatient,
    refetch: fetchPatients
  }
}