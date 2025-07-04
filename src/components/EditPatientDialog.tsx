import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Save, Plus, Loader2 } from 'lucide-react';
import { usePatients } from '@/hooks/usePatients';
import { useSpecialites } from '@/hooks/useSpecialites';
import PatientSpecialitesManager from './PatientSpecialitesManager';
import type { Patient } from '@/lib/supabase';

interface EditPatientDialogProps {
  patient: Patient | null;
  isOpen: boolean;
  onClose: () => void;
}

const EditPatientDialog = ({ patient, isOpen, onClose }: EditPatientDialogProps) => {
  const { updatePatient } = usePatients();
  const { specialites, addSpecialite } = useSpecialites();
  
  const [formData, setFormData] = useState({
    prenom: '',
    nom: '',
    age: '',
    glycemie: '',
    ta: '',
    taille: '',
    poids: '',
    specialite: '',
    medicaments: '',
    notes: ''
  });
  
  const [newSpecialite, setNewSpecialite] = useState('');
  const [showAddSpecialite, setShowAddSpecialite] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAddingSpecialite, setIsAddingSpecialite] = useState(false);

  useEffect(() => {
    if (patient) {
      setFormData({
        prenom: patient.prenom,
        nom: patient.nom,
        age: patient.age.toString(),
        glycemie: patient.glycemie,
        ta: patient.ta,
        taille: patient.taille.toString(),
        poids: patient.poids.toString(),
        specialite: patient.specialite,
        medicaments: patient.medicaments,
        notes: patient.notes
      });
    }
  }, [patient]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculateIMC = () => {
    const poids = parseFloat(formData.poids);
    const taille = parseFloat(formData.taille) / 100;
    
    if (poids && taille) {
      return (poids / (taille * taille)).toFixed(2);
    }
    return '';
  };

  const handleAddSpecialite = async () => {
    if (!newSpecialite.trim()) return;
    
    try {
      setIsAddingSpecialite(true);
      await addSpecialite(newSpecialite.trim());
      setFormData(prev => ({ ...prev, specialite: newSpecialite.trim() }));
      setNewSpecialite('');
      setShowAddSpecialite(false);
    } catch (error) {
      // Error is handled in the hook
    } finally {
      setIsAddingSpecialite(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!patient) return;

    try {
      setIsSubmitting(true);
      const imc = calculateIMC();
      
      await updatePatient(patient.id, {
        prenom: formData.prenom,
        nom: formData.nom,
        age: parseInt(formData.age),
        glycemie: formData.glycemie,
        ta: formData.ta,
        taille: parseFloat(formData.taille) || 0,
        poids: parseFloat(formData.poids) || 0,
        imc: parseFloat(imc) || 0,
        specialite: formData.specialite,
        medicaments: formData.medicaments,
        notes: formData.notes,
      });

      onClose();
    } catch (error) {
      // Error is handled in the hook
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            Modifier Patient - {patient?.prenom} {patient?.nom}
          </DialogTitle>
        </DialogHeader>
        
        <Tabs defaultValue="info" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="info">Informations Patient</TabsTrigger>
            <TabsTrigger value="specialites">Gestion Spécialités</TabsTrigger>
          </TabsList>
          
          <TabsContent value="info" className="space-y-6 mt-4">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Informations personnelles */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="prenom" className="text-sm font-medium text-gray-700">
                    Prénom *
                  </Label>
                  <Input
                    id="prenom"
                    value={formData.prenom}
                    onChange={(e) => handleInputChange('prenom', e.target.value)}
                    className="mt-1 border-blue-200 focus:border-blue-500"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="nom" className="text-sm font-medium text-gray-700">
                    Nom *
                  </Label>
                  <Input
                    id="nom"
                    value={formData.nom}
                    onChange={(e) => handleInputChange('nom', e.target.value)}
                    className="mt-1 border-blue-200 focus:border-blue-500"
                    required
                  />
                </div>
              </div>

              {/* Données médicales */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="age" className="text-sm font-medium text-gray-700">
                    Âge *
                  </Label>
                  <Input
                    id="age"
                    type="number"
                    value={formData.age}
                    onChange={(e) => handleInputChange('age', e.target.value)}
                    className="mt-1 border-red-200 focus:border-red-500"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="glycemie" className="text-sm font-medium text-gray-700">
                    Glycémie
                  </Label>
                  <Input
                    id="glycemie"
                    value={formData.glycemie}
                    onChange={(e) => handleInputChange('glycemie', e.target.value)}
                    className="mt-1 border-red-200 focus:border-red-500"
                  />
                </div>
                
                <div>
                  <Label htmlFor="ta" className="text-sm font-medium text-gray-700">
                    Tension Artérielle
                  </Label>
                  <Input
                    id="ta"
                    placeholder="ex: 120/80"
                    value={formData.ta}
                    onChange={(e) => handleInputChange('ta', e.target.value)}
                    className="mt-1 border-red-200 focus:border-red-500"
                  />
                </div>
              </div>

              {/* Mesures physiques */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="taille" className="text-sm font-medium text-gray-700">
                    Taille (cm)
                  </Label>
                  <Input
                    id="taille"
                    type="number"
                    step="0.1"
                    value={formData.taille}
                    onChange={(e) => handleInputChange('taille', e.target.value)}
                    className="mt-1 border-blue-200 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <Label htmlFor="poids" className="text-sm font-medium text-gray-700">
                    Poids (kg)
                  </Label>
                  <Input
                    id="poids"
                    type="number"
                    step="0.1"
                    value={formData.poids}
                    onChange={(e) => handleInputChange('poids', e.target.value)}
                    className="mt-1 border-blue-200 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-700">
                    IMC (calculé)
                  </Label>
                  <div className="mt-1 p-2 bg-gray-50 border rounded-md text-sm font-medium">
                    {calculateIMC() || 'En attente...'}
                  </div>
                </div>
              </div>

              {/* Spécialité principale avec option d'ajout */}
              <div>
                <Label htmlFor="specialite" className="text-sm font-medium text-gray-700">
                  Spécialité principale *
                </Label>
                <div className="flex gap-2 mt-1">
                  <Select value={formData.specialite} onValueChange={(value) => handleInputChange('specialite', value)}>
                    <SelectTrigger className="border-blue-200 focus:border-blue-500">
                      <SelectValue placeholder="Sélectionner une spécialité" />
                    </SelectTrigger>
                    <SelectContent>
                      {specialites.map((spec) => (
                        <SelectItem key={spec.id} value={spec.nom}>
                          {spec.nom}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowAddSpecialite(!showAddSpecialite)}
                    className="px-3"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                
                {showAddSpecialite && (
                  <div className="flex gap-2 mt-2">
                    <Input
                      placeholder="Nouvelle spécialité"
                      value={newSpecialite}
                      onChange={(e) => setNewSpecialite(e.target.value)}
                      className="border-green-200 focus:border-green-500"
                    />
                    <Button
                      type="button"
                      onClick={handleAddSpecialite}
                      disabled={isAddingSpecialite}
                      className="bg-green-500 hover:bg-green-600"
                    >
                      {isAddingSpecialite ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        'Ajouter'
                      )}
                    </Button>
                  </div>
                )}
              </div>

              {/* Médicaments */}
              <div>
                <Label htmlFor="medicaments" className="text-sm font-medium text-gray-700">
                  Médicaments prescrits
                </Label>
                <Textarea
                  id="medicaments"
                  value={formData.medicaments}
                  onChange={(e) => handleInputChange('medicaments', e.target.value)}
                  className="mt-1 border-blue-200 focus:border-blue-500"
                  rows={3}
                  placeholder="Liste des médicaments et posologies..."
                />
              </div>

              {/* Notes */}
              <div>
                <Label htmlFor="notes" className="text-sm font-medium text-gray-700">
                  Notes médicales
                </Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  className="mt-1 border-blue-200 focus:border-blue-500"
                  rows={4}
                  placeholder="Observations, diagnostics, recommandations..."
                />
              </div>

              <div className="flex gap-3">
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium py-3"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Sauvegarde...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Sauvegarder les Modifications
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={onClose}
                  className="px-6"
                >
                  Annuler
                </Button>
              </div>
            </form>
          </TabsContent>
          
          <TabsContent value="specialites" className="mt-4">
            {patient && <PatientSpecialitesManager patient={patient} />}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default EditPatientDialog;