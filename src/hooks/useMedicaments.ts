import { useState, useEffect, useCallback } from 'react'
import { supabase } from '@/integrations/supabase/client'
import type { Medicament, FamilleMedicament } from '@/types/database'
import { useToast } from '@/hooks/use-toast'

export const useMedicaments = () => {
  const [medicaments, setMedicaments] = useState<Medicament[]>([])
  const [familles, setFamilles] = useState<FamilleMedicament[]>([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  const fetchMedicaments = useCallback(async () => {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('medicaments')
        .select(`
          *,
          famille:famille_medicaments (
            id,
            nom,
            description,
            created_at
          )
        `)
        .order('nom', { ascending: true })

      if (error) throw error
      setMedicaments(data || [])
    } catch (error) {
      console.error('Error fetching medicaments:', error)
      toast({
        title: "Erreur",
        description: "Impossible de charger les médicaments",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }, [toast])

  const fetchFamilles = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('famille_medicaments')
        .select(`
          *,
          medicaments (*)
        `)
        .order('nom', { ascending: true })

      if (error) throw error
      setFamilles(data || [])
    } catch (error) {
      console.error('Error fetching familles:', error)
      toast({
        title: "Erreur",
        description: "Impossible de charger les familles de médicaments",
        variant: "destructive"
      })
    }
  }, [toast])

  const addMedicament = async (medicamentData: Omit<Medicament, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const { data, error } = await supabase
        .from('medicaments')
        .insert([medicamentData])
        .select(`
          *,
          famille:famille_medicaments (
            id,
            nom,
            description,
            created_at
          )
        `)
        .single()

      if (error) throw error
      
      setMedicaments(prev => [...prev, data].sort((a, b) => a.nom.localeCompare(b.nom)))
      toast({
        title: "Médicament ajouté",
        description: `${data.nom} a été ajouté avec succès.`
      })
      return data
    } catch (error) {
      console.error('Error adding medicament:', error)
      toast({
        title: "Erreur",
        description: "Impossible d'ajouter le médicament",
        variant: "destructive"
      })
      throw error
    }
  }

  const updateMedicament = async (id: string, medicamentData: Partial<Medicament>) => {
    try {
      const { data, error } = await supabase
        .from('medicaments')
        .update(medicamentData)
        .eq('id', id)
        .select(`
          *,
          famille:famille_medicaments (
            id,
            nom,
            description,
            created_at
          )
        `)
        .single()

      if (error) throw error

      setMedicaments(prev => 
        prev.map(m => m.id === id ? data : m).sort((a, b) => a.nom.localeCompare(b.nom))
      )
      toast({
        title: "Médicament modifié",
        description: `${data.nom} a été modifié avec succès.`
      })
      return data
    } catch (error) {
      console.error('Error updating medicament:', error)
      toast({
        title: "Erreur",
        description: "Impossible de modifier le médicament",
        variant: "destructive"
      })
      throw error
    }
  }

  const updateStock = async (id: string, nouvelleQuantite: number) => {
    try {
      const { data, error } = await supabase
        .from('medicaments')
        .update({ stock_actuel: nouvelleQuantite })
        .eq('id', id)
        .select(`
          *,
          famille:famille_medicaments (
            id,
            nom,
            description,
            created_at
          )
        `)
        .single()

      if (error) throw error

      setMedicaments(prev => 
        prev.map(m => m.id === id ? data : m)
      )
      toast({
        title: "Stock mis à jour",
        description: `Stock de ${data.nom} mis à jour: ${nouvelleQuantite} unités.`
      })
      return data
    } catch (error) {
      console.error('Error updating stock:', error)
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour le stock",
        variant: "destructive"
      })
      throw error
    }
  }

  const deleteMedicament = async (id: string) => {
    try {
      const { error } = await supabase
        .from('medicaments')
        .delete()
        .eq('id', id)

      if (error) throw error

      setMedicaments(prev => prev.filter(m => m.id !== id))
      toast({
        title: "Médicament supprimé",
        description: "Le médicament a été supprimé avec succès."
      })
    } catch (error) {
      console.error('Error deleting medicament:', error)
      toast({
        title: "Erreur",
        description: "Impossible de supprimer le médicament",
        variant: "destructive"
      })
      throw error
    }
  }

  const addFamille = async (nom: string, description: string = '') => {
    try {
      const { data, error } = await supabase
        .from('famille_medicaments')
        .insert([{ nom: nom.trim(), description: description.trim() }])
        .select()
        .single()

      if (error) throw error
      
      setFamilles(prev => [...prev, data].sort((a, b) => a.nom.localeCompare(b.nom)))
      toast({
        title: "Famille ajoutée",
        description: `La famille "${data.nom}" a été ajoutée avec succès.`
      })
      return data
    } catch (error) {
      console.error('Error adding famille:', error)
      if (error.code === '23505') {
        toast({
          title: "Erreur",
          description: "Cette famille de médicaments existe déjà",
          variant: "destructive"
        })
      } else {
        toast({
          title: "Erreur",
          description: "Impossible d'ajouter la famille de médicaments",
          variant: "destructive"
        })
      }
      throw error
    }
  }

  useEffect(() => {
    fetchMedicaments()
    fetchFamilles()

    // Set up real-time subscription
    const medicamentsSubscription = supabase
      .channel('medicaments_changes')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'medicaments' },
        () => fetchMedicaments()
      )
      .subscribe()

    const famillesSubscription = supabase
      .channel('familles_changes')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'famille_medicaments' },
        () => fetchFamilles()
      )
      .subscribe()

    return () => {
      medicamentsSubscription.unsubscribe()
      famillesSubscription.unsubscribe()
    }
  }, [fetchMedicaments, fetchFamilles])

  return {
    medicaments,
    familles,
    loading,
    addMedicament,
    updateMedicament,
    updateStock,
    deleteMedicament,
    addFamille,
    refetch: () => {
      fetchMedicaments()
      fetchFamilles()
    }
  }
}