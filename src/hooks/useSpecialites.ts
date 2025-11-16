import { useState, useEffect } from 'react'
import { supabase } from '@/integrations/supabase/client'
import type { Specialite } from '@/types/database'
import { useToast } from '@/hooks/use-toast'

export const useSpecialites = () => {
  const [specialites, setSpecialites] = useState<Specialite[]>([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  const fetchSpecialites = async () => {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('specialites')
        .select('*')
        .order('nom', { ascending: true })

      if (error) throw error
      setSpecialites(data || [])
    } catch (error) {
      console.error('Error fetching specialites:', error)
      toast({
        title: "Erreur",
        description: "Impossible de charger les spécialités",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const addSpecialite = async (nom: string) => {
    try {
      const { data, error } = await supabase
        .from('specialites')
        .insert([{ nom: nom.trim() }])
        .select()
        .single()

      if (error) throw error
      
      setSpecialites(prev => [...prev, data].sort((a, b) => a.nom.localeCompare(b.nom)))
      toast({
        title: "Spécialité ajoutée",
        description: `La spécialité "${data.nom}" a été ajoutée avec succès.`
      })
      return data
    } catch (error) {
      console.error('Error adding specialite:', error)
      if (error.code === '23505') {
        toast({
          title: "Erreur",
          description: "Cette spécialité existe déjà",
          variant: "destructive"
        })
      } else {
        toast({
          title: "Erreur",
          description: "Impossible d'ajouter la spécialité",
          variant: "destructive"
        })
      }
      throw error
    }
  }

  const deleteSpecialite = async (id: string) => {
    try {
      const { error } = await supabase
        .from('specialites')
        .delete()
        .eq('id', id)

      if (error) throw error

      setSpecialites(prev => prev.filter(s => s.id !== id))
      toast({
        title: "Spécialité supprimée",
        description: "La spécialité a été supprimée avec succès."
      })
    } catch (error) {
      console.error('Error deleting specialite:', error)
      toast({
        title: "Erreur",
        description: "Impossible de supprimer la spécialité",
        variant: "destructive"
      })
      throw error
    }
  }

  useEffect(() => {
    fetchSpecialites()

    // Set up real-time subscription
    const subscription = supabase
      .channel('specialites_changes')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'specialites' },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setSpecialites(prev => [...prev, payload.new as Specialite].sort((a, b) => a.nom.localeCompare(b.nom)))
          } else if (payload.eventType === 'DELETE') {
            setSpecialites(prev => prev.filter(s => s.id !== payload.old.id))
          }
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  return {
    specialites,
    loading,
    addSpecialite,
    deleteSpecialite,
    refetch: fetchSpecialites
  }
}