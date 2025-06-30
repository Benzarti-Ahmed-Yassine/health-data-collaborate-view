import { useState, useEffect } from 'react'
import { supabase, type Specialite } from '@/lib/supabase'
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
    refetch: fetchSpecialites
  }
}