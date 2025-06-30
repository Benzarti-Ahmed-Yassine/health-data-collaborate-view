import { useState, useEffect } from 'react'
import { supabase, type Patient } from '@/lib/supabase'
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
        .select('*')
        .order('created_at', { ascending: false })

      if (error) throw error
      setPatients(data || [])
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
      
      setPatients(prev => [data, ...prev])
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

      setPatients(prev => prev.map(p => p.id === id ? data : p))
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

  useEffect(() => {
    fetchPatients()

    // Set up real-time subscription
    const subscription = supabase
      .channel('patients_changes')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'patients' },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setPatients(prev => [payload.new as Patient, ...prev])
          } else if (payload.eventType === 'UPDATE') {
            setPatients(prev => prev.map(p => 
              p.id === payload.new.id ? payload.new as Patient : p
            ))
          } else if (payload.eventType === 'DELETE') {
            setPatients(prev => prev.filter(p => p.id !== payload.old.id))
          }
        }
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
    refetch: fetchPatients
  }
}