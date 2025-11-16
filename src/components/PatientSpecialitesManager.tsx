import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus, X, Trash2, Loader2, Save, Download } from 'lucide-react';
import { useSpecialites } from '@/hooks/useSpecialites';
import { usePatients } from '@/hooks/usePatients';
import type { Patient, Specialite } from '@/types/database';

interface PatientSpecialitesManagerProps {
  patient: Patient;
}

const PatientSpecialitesManager = ({ patient }: PatientSpecialitesManagerProps) => {
  const { specialites, deleteSpecialite } = useSpecialites();
  const { addSpecialiteToPatient, removeSpecialiteFromPatient } = usePatients();
  const [selectedSpecialiteIds, setSelectedSpecialiteIds] = useState<string[]>([]);
  const [selectedForRemoval, setSelectedForRemoval] = useState<string[]>([]);
  const [selectedForDeletion, setSelectedForDeletion] = useState<string[]>([]);
  const [isAssigning, setIsAssigning] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

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

  const handleRemovalSelection = (specialiteId: string, checked: boolean) => {
    if (checked) {
      setSelectedForRemoval(prev => [...prev, specialiteId]);
    } else {
      setSelectedForRemoval(prev => prev.filter(id => id !== specialiteId));
    }
  };

  const handleDeletionSelection = (specialiteId: string, checked: boolean) => {
    if (checked) {
      setSelectedForDeletion(prev => [...prev, specialiteId]);
    } else {
      setSelectedForDeletion(prev => prev.filter(id => id !== specialiteId));
    }
  };

  const handleAssignMultipleSpecialites = async () => {
    if (selectedSpecialiteIds.length === 0) return;
    
    try {
      setIsAssigning(true);
      
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

  const handleRemoveMultipleSpecialites = async () => {
    if (selectedForRemoval.length === 0) return;
    
    try {
      setIsRemoving(true);
      
      for (const specialiteId of selectedForRemoval) {
        await removeSpecialiteFromPatient(patient.id, specialiteId);
      }
      
      setSelectedForRemoval([]);
    } catch (error) {
      // Error handled in hook
    } finally {
      setIsRemoving(false);
    }
  };

  const handleDeleteMultipleSpecialites = async () => {
    if (selectedForDeletion.length === 0) return;
    
    try {
      setIsDeleting(true);
      
      for (const specialiteId of selectedForDeletion) {
        await deleteSpecialite(specialiteId);
      }
      
      setSelectedForDeletion([]);
    } catch (error) {
      // Error handled in hook
    } finally {
      setIsDeleting(false);
    }
  };

  const selectAllAvailable = () => {
    setSelectedSpecialiteIds(availableSpecialites.map(spec => spec.id));
  };

  const selectAllAssigned = () => {
    setSelectedForRemoval(patientSpecialites.map(spec => spec.id));
  };

  const selectAllForDeletion = () => {
    setSelectedForDeletion(specialites.map(spec => spec.id));
  };

  const clearSelection = () => {
    setSelectedSpecialiteIds([]);
  };

  const clearRemovalSelection = () => {
    setSelectedForRemoval([]);
  };

  const clearDeletionSelection = () => {
    setSelectedForDeletion([]);
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
          {/* Spécialités actuelles du patient avec suppression sélective */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">
                Spécialités assignées ({patientSpecialites.length})
              </h3>
              {patientSpecialites.length > 0 && (
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={selectAllAssigned}
                    disabled={selectedForRemoval.length === patientSpecialites.length}
                  >
                    Tout sélectionner
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearRemovalSelection}
                    disabled={selectedForRemoval.length === 0}
                  >
                    Tout désélectionner
                  </Button>
                </div>
              )}
            </div>

            {patientSpecialites.length === 0 ? (
              <p className="text-gray-500 italic">Aucune spécialité assignée</p>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
                  {patientSpecialites.map((specialite) => (
                    <div key={specialite.id} className="flex items-center space-x-2 p-2 border rounded hover:bg-red-50">
                      <Checkbox
                        id={`remove-${specialite.id}`}
                        checked={selectedForRemoval.includes(specialite.id)}
                        onCheckedChange={(checked) => 
                          handleRemovalSelection(specialite.id, checked as boolean)
                        }
                      />
                      <label 
                        htmlFor={`remove-${specialite.id}`}
                        className="text-sm font-medium cursor-pointer flex-1"
                      >
                        {specialite.nom}
                      </label>
                    </div>
                  ))}
                </div>

                {selectedForRemoval.length > 0 && (
                  <Button
                    onClick={handleRemoveMultipleSpecialites}
                    disabled={isRemoving}
                    variant="destructive"
                    className="w-full"
                  >
                    {isRemoving ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Suppression en cours...
                      </>
                    ) : (
                      <>
                        <Trash2 className="h-4 w-4 mr-2" />
                        Supprimer {selectedForRemoval.length} spécialité(s) du patient
                      </>
                    )}
                  </Button>
                )}
              </>
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
                  <div key={specialite.id} className="flex items-center space-x-2 p-2 border rounded hover:bg-green-50">
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

              {selectedSpecialiteIds.length > 0 && (
                <Button
                  onClick={handleAssignMultipleSpecialites}
                  disabled={isAssigning}
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
              )}
            </div>
          )}

          {availableSpecialites.length === 0 && (
            <div className="text-center py-4">
              <p className="text-gray-500">Toutes les spécialités disponibles sont déjà assignées à ce patient.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Gestion des spécialités globales avec suppression sélective */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Trash2 className="h-5 w-5 text-red-600" />
            <span>Suppression de Spécialités Globales</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-600">
              Sélectionnez les spécialités à supprimer définitivement du système
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={selectAllForDeletion}
                disabled={selectedForDeletion.length === specialites.length}
              >
                Tout sélectionner
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={clearDeletionSelection}
                disabled={selectedForDeletion.length === 0}
              >
                Tout désélectionner
              </Button>
            </div>
          </div>

          <div className="max-h-60 overflow-y-auto space-y-2 mb-4">
            {specialites.map((specialite) => (
              <div key={specialite.id} className="flex items-center space-x-3 p-3 border rounded hover:bg-red-50">
                <Checkbox
                  id={`delete-${specialite.id}`}
                  checked={selectedForDeletion.includes(specialite.id)}
                  onCheckedChange={(checked) => 
                    handleDeletionSelection(specialite.id, checked as boolean)
                  }
                />
                <label 
                  htmlFor={`delete-${specialite.id}`}
                  className="text-sm font-medium cursor-pointer flex-1"
                >
                  {specialite.nom}
                </label>
                {patientSpecialites.some(ps => ps.id === specialite.id) && (
                  <Badge variant="secondary" className="text-xs">
                    Assignée
                  </Badge>
                )}
              </div>
            ))}
          </div>

          {selectedForDeletion.length > 0 && (
            <Button
              onClick={handleDeleteMultipleSpecialites}
              disabled={isDeleting}
              variant="destructive"
              className="w-full"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Suppression en cours...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Supprimer définitivement {selectedForDeletion.length} spécialité(s)
                </>
              )}
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PatientSpecialitesManager;