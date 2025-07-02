import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Plus, X, Trash2, Loader2 } from 'lucide-react';
import { useSpecialites } from '@/hooks/useSpecialites';
import { usePatients } from '@/hooks/usePatients';
import type { Patient, Specialite } from '@/lib/supabase';

interface PatientSpecialitesManagerProps {
  patient: Patient;
}

const PatientSpecialitesManager = ({ patient }: PatientSpecialitesManagerProps) => {
  const { specialites, deleteSpecialite } = useSpecialites();
  const { addSpecialiteToPatient, removeSpecialiteFromPatient } = usePatients();
  const [selectedSpecialiteId, setSelectedSpecialiteId] = useState<string>('');
  const [isAdding, setIsAdding] = useState(false);
  const [removingId, setRemovingId] = useState<string | null>(null);
  const [deletingSpecialiteId, setDeletingSpecialiteId] = useState<string | null>(null);

  const patientSpecialites = patient.specialites || [];
  const availableSpecialites = specialites.filter(
    spec => !patientSpecialites.some(ps => ps.id === spec.id)
  );

  const handleAddSpecialite = async () => {
    if (!selectedSpecialiteId) return;
    
    try {
      setIsAdding(true);
      await addSpecialiteToPatient(patient.id, selectedSpecialiteId);
      setSelectedSpecialiteId('');
    } catch (error) {
      // Error handled in hook
    } finally {
      setIsAdding(false);
    }
  };

  const handleRemoveSpecialite = async (specialiteId: string) => {
    try {
      setRemovingId(specialiteId);
      await removeSpecialiteFromPatient(patient.id, specialiteId);
    } catch (error) {
      // Error handled in hook
    } finally {
      setRemovingId(null);
    }
  };

  const handleDeleteSpecialite = async (specialiteId: string) => {
    try {
      setDeletingSpecialiteId(specialiteId);
      await deleteSpecialite(specialiteId);
    } catch (error) {
      // Error handled in hook
    } finally {
      setDeletingSpecialiteId(null);
    }
  };

  return (
    <Card className="border-purple-200 shadow-lg">
      <CardHeader className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
        <CardTitle className="flex items-center space-x-2">
          <Plus className="h-5 w-5" />
          <span>Gestion des Spécialités</span>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-6 space-y-6">
        {/* Spécialités actuelles du patient */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Spécialités assignées</h3>
          {patientSpecialites.length === 0 ? (
            <p className="text-gray-500 italic">Aucune spécialité assignée</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {patientSpecialites.map((specialite) => (
                <Badge 
                  key={specialite.id} 
                  variant="default" 
                  className="flex items-center space-x-2 px-3 py-1"
                >
                  <span>{specialite.nom}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveSpecialite(specialite.id)}
                    disabled={removingId === specialite.id}
                    className="h-4 w-4 p-0 hover:bg-red-100"
                  >
                    {removingId === specialite.id ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      <X className="h-3 w-3" />
                    )}
                  </Button>
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Ajouter une nouvelle spécialité */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Ajouter une spécialité</h3>
          <div className="flex gap-2">
            <Select value={selectedSpecialiteId} onValueChange={setSelectedSpecialiteId}>
              <SelectTrigger className="flex-1">
                <SelectValue placeholder="Sélectionner une spécialité" />
              </SelectTrigger>
              <SelectContent>
                {availableSpecialites.map((specialite) => (
                  <SelectItem key={specialite.id} value={specialite.id}>
                    {specialite.nom}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              onClick={handleAddSpecialite}
              disabled={!selectedSpecialiteId || isAdding}
              className="bg-green-500 hover:bg-green-600"
            >
              {isAdding ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Gestion des spécialités globales */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Toutes les spécialités disponibles</h3>
          <div className="max-h-40 overflow-y-auto space-y-2">
            {specialites.map((specialite) => (
              <div key={specialite.id} className="flex items-center justify-between p-2 border rounded">
                <span className="text-sm">{specialite.nom}</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDeleteSpecialite(specialite.id)}
                  disabled={deletingSpecialiteId === specialite.id}
                  className="text-red-600 hover:bg-red-50"
                >
                  {deletingSpecialiteId === specialite.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                </Button>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PatientSpecialitesManager;