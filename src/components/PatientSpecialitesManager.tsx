import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus, X, Trash2, Loader2, Save } from 'lucide-react';
import { useSpecialites } from '@/hooks/useSpecialites';
import { usePatients } from '@/hooks/usePatients';
import type { Patient, Specialite } from '@/lib/supabase';

interface PatientSpecialitesManagerProps {
  patient: Patient;
}

const PatientSpecialitesManager = ({ patient }: PatientSpecialitesManagerProps) => {
  const { specialites, deleteSpecialite } = useSpecialites();
  const { addSpecialiteToPatient, removeSpecialiteFromPatient } = usePatients();
  const [selectedSpecialiteIds, setSelectedSpecialiteIds] = useState<string[]>([]);
  const [isAssigning, setIsAssigning] = useState(false);
  const [removingId, setRemovingId] = useState<string | null>(null);
  const [deletingSpecialiteId, setDeletingSpecialiteId] = useState<string | null>(null);

  const patientSpecialites = patient.specialites || [];
  const availableSpecialites = specialites.filter(
    spec => !patientSpecialites.some(ps => ps.id === spec.id)
  );

  const handleSpecialiteSelection = (specialiteId: string, checked: boolean) => {
    if (checked) {
      setSelectedSpecialiteIds(prev => [...prev, specialiteId]);
    } else {
      setSelectedSpecialiteIds(prev => prev.filter(id => id !== specialiteId));
    }
  };

  const handleAssignMultipleSpecialites = async () => {
    if (selectedSpecialiteIds.length === 0) return;
    
    try {
      setIsAssigning(true);
      
      // Assigner toutes les spécialités sélectionnées
      for (const specialiteId of selectedSpecialiteIds) {
        await addSpecialiteToPatient(patient.id, specialiteId);
      }
      
      setSelectedSpecialiteIds([]);
    } catch (error) {
      // Error handled in hook
    } finally {
      setIsAssigning(false);
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

  const selectAllAvailable = () => {
    setSelectedSpecialiteIds(availableSpecialites.map(spec => spec.id));
  };

  const clearSelection = () => {
    setSelectedSpecialiteIds([]);
  };

  return (
    <div className="space-y-6">
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
            <h3 className="text-lg font-semibold mb-3">Spécialités assignées ({patientSpecialites.length})</h3>
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

          {/* Assignation multiple de spécialités */}
          {availableSpecialites.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold">
                  Assigner des spécialités ({selectedSpecialiteIds.length} sélectionnées)
                </h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={selectAllAvailable}
                    disabled={selectedSpecialiteIds.length === availableSpecialites.length}
                  >
                    Tout sélectionner
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearSelection}
                    disabled={selectedSpecialiteIds.length === 0}
                  >
                    Tout désélectionner
                  </Button>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
                {availableSpecialites.map((specialite) => (
                  <div key={specialite.id} className="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50">
                    <Checkbox
                      id={`spec-${specialite.id}`}
                      checked={selectedSpecialiteIds.includes(specialite.id)}
                      onCheckedChange={(checked) => 
                        handleSpecialiteSelection(specialite.id, checked as boolean)
                      }
                    />
                    <label 
                      htmlFor={`spec-${specialite.id}`}
                      className="text-sm font-medium cursor-pointer flex-1"
                    >
                      {specialite.nom}
                    </label>
                  </div>
                ))}
              </div>

              <Button
                onClick={handleAssignMultipleSpecialites}
                disabled={selectedSpecialiteIds.length === 0 || isAssigning}
                className="w-full bg-green-500 hover:bg-green-600"
              >
                {isAssigning ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Assignation en cours...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Assigner {selectedSpecialiteIds.length} spécialité(s)
                  </>
                )}
              </Button>
            </div>
          )}

          {availableSpecialites.length === 0 && (
            <div className="text-center py-4">
              <p className="text-gray-500">Toutes les spécialités disponibles sont déjà assignées à ce patient.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Gestion des spécialités globales */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Trash2 className="h-5 w-5 text-red-600" />
            <span>Gestion des Spécialités Globales</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="max-h-60 overflow-y-auto space-y-2">
            {specialites.map((specialite) => (
              <div key={specialite.id} className="flex items-center justify-between p-3 border rounded hover:bg-gray-50">
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-medium">{specialite.nom}</span>
                  {patientSpecialites.some(ps => ps.id === specialite.id) && (
                    <Badge variant="secondary" className="text-xs">
                      Assignée
                    </Badge>
                  )}
                </div>
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
        </CardContent>
      </Card>
    </div>
  );
};

export default PatientSpecialitesManager;