import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { UserPlus, Save, Plus, Loader2, Trash2, Heart } from 'lucide-react';
import { usePatients } from '@/hooks/usePatients';
import { useSpecialites } from '@/hooks/useSpecialites';

const PatientForm = () => {
  const { addPatient, addSpecialiteToPatient } = usePatients();
  const { specialites, addSpecialite, deleteSpecialite } = useSpecialites();
  
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
  
  const [selectedSpecialiteIds, setSelectedSpecialiteIds] = useState<string[]>([]);
  const [selectedForDeletion, setSelectedForDeletion] = useState<string[]>([]);
  const [newSpecialite, setNewSpecialite] = useState('');
  const [showAddSpecialite, setShowAddSpecialite] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAddingSpecialite, setIsAddingSpecialite] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSpecialiteSelection = (specialiteId: string, checked: boolean) => {
    if (checked) {
      setSelectedSpecialiteIds(prev => [...prev, specialiteId]);
    } else {
      setSelectedSpecialiteIds(prev => prev.filter(id => id !== specialiteId));
    }
  };

  const handleDeletionSelection = (specialiteId: string, checked: boolean) => {
    if (checked) {
      setSelectedForDeletion(prev => [...prev, specialiteId]);
    } else {
      setSelectedForDeletion(prev => prev.filter(id => id !== specialiteId));
    }
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
      const newSpec = await addSpecialite(newSpecialite.trim());
      setFormData(prev => ({ ...prev, specialite: newSpecialite.trim() }));
      setSelectedSpecialiteIds(prev => [...prev, newSpec.id]);
      setNewSpecialite('');
      setShowAddSpecialite(false);
    } catch (error) {
      // Error is handled in the hook
    } finally {
      setIsAddingSpecialite(false);
    }
  };

  const handleDeleteSpecialites = async () => {
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

  const selectAllSpecialites = () => {
    setSelectedSpecialiteIds(specialites.map(spec => spec.id));
  };

  const clearSpecialiteSelection = () => {
    setSelectedSpecialiteIds([]);
  };

  const selectAllForDeletion = () => {
    setSelectedForDeletion(specialites.map(spec => spec.id));
  };

  const clearDeletionSelection = () => {
    setSelectedForDeletion([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setIsSubmitting(true);
      const imc = calculateIMC();
      
      // Créer le patient
      const newPatient = await addPatient({
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

      // Assigner toutes les spécialités sélectionnées
      for (const specialiteId of selectedSpecialiteIds) {
        await addSpecialiteToPatient(newPatient.id, specialiteId);
      }

      // Reset form
      setFormData({
        prenom: '', nom: '', age: '', glycemie: '', ta: '', taille: '', poids: '',
        specialite: '', medicaments: '', notes: ''
      });
      setSelectedSpecialiteIds([]);
    } catch (error) {
      // Error is handled in the hook
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in-up">
      <Card className="border-primary/20 shadow-xl card-hover">
        <CardHeader className="medical-gradient text-white">
          <CardTitle className="flex items-center space-x-3">
            <img 
              src="/2.png" 
              alt="PAR'ACT Logo" 
              className="h-8 w-8 object-contain bg-white rounded-full p-1"
            />
            <Heart className="h-6 w-6 animate-pulse-slow" />
            <UserPlus className="h-6 w-6" />
            <span>Fiche du Patient</span>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Informations personnelles */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="animate-slide-in-left delay-100">
                <Label htmlFor="prenom" className="text-sm font-medium text-gray-700">
                  Prénom *
                </Label>
                <Input
                  id="prenom"
                  value={formData.prenom}
                  onChange={(e) => handleInputChange('prenom', e.target.value)}
                  className="mt-1 border-primary/30 focus:border-primary smooth-transition"
                  required
                />
              </div>
              
              <div className="animate-slide-in-right delay-100">
                <Label htmlFor="nom" className="text-sm font-medium text-gray-700">
                  Nom *
                </Label>
                <Input
                  id="nom"
                  value={formData.nom}
                  onChange={(e) => handleInputChange('nom', e.target.value)}
                  className="mt-1 border-primary/30 focus:border-primary smooth-transition"
                  required
                />
              </div>
            </div>

            {/* Données médicales */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-fade-in-up delay-200">
              <div>
                <Label htmlFor="age" className="text-sm font-medium text-gray-700">
                  Âge *
                </Label>
                <Input
                  id="age"
                  type="number"
                  value={formData.age}
                  onChange={(e) => handleInputChange('age', e.target.value)}
                  className="mt-1 border-red-200 focus:border-red-500 smooth-transition"
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
                  className="mt-1 border-red-200 focus:border-red-500 smooth-transition"
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
                  className="mt-1 border-red-200 focus:border-red-500 smooth-transition"
                />
              </div>
            </div>

            {/* Mesures physiques */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-fade-in-up delay-300">
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
                  className="mt-1 border-primary/30 focus:border-primary smooth-transition"
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
                  className="mt-1 border-primary/30 focus:border-primary smooth-transition"
                />
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-700">
                  IMC (calculé)
                </Label>
                <div className="mt-1 p-2 bg-red-50 border border-red-200 rounded-md text-sm font-medium text-primary">
                  {calculateIMC() || 'En attente...'}
                </div>
              </div>
            </div>

            {/* Spécialité principale avec option d'ajout */}
            <div className="animate-fade-in-up delay-400">
              <Label htmlFor="specialite" className="text-sm font-medium text-gray-700">
                Spécialité principale *
              </Label>
              <div className="flex gap-2 mt-1">
                <Select value={formData.specialite} onValueChange={(value) => handleInputChange('specialite', value)}>
                  <SelectTrigger className="border-primary/30 focus:border-primary smooth-transition">
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
                  className="px-3 border-primary/30 hover:bg-red-50 smooth-transition"
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              
              {showAddSpecialite && (
                <div className="flex gap-2 mt-2 animate-scale-in">
                  <Input
                    placeholder="Nouvelle spécialité"
                    value={newSpecialite}
                    onChange={(e) => setNewSpecialite(e.target.value)}
                    className="border-green-200 focus:border-green-500 smooth-transition"
                  />
                  <Button
                    type="button"
                    onClick={handleAddSpecialite}
                    disabled={isAddingSpecialite}
                    className="bg-green-500 hover:bg-green-600 smooth-transition"
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

            {/* Spécialités multiples */}
            <div className="animate-fade-in-up delay-500">
              <div className="flex items-center justify-between mb-3">
                <Label className="text-sm font-medium text-gray-700">
                  Spécialités supplémentaires ({selectedSpecialiteIds.length} sélectionnées)
                </Label>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={selectAllSpecialites}
                    disabled={selectedSpecialiteIds.length === specialites.length}
                    className="smooth-transition hover:bg-red-50"
                  >
                    Tout sélectionner
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={clearSpecialiteSelection}
                    disabled={selectedSpecialiteIds.length === 0}
                    className="smooth-transition hover:bg-red-50"
                  >
                    Tout désélectionner
                  </Button>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 p-4 border rounded-lg bg-red-50/50">
                {specialites.map((specialite, index) => (
                  <div key={specialite.id} className={`flex items-center space-x-2 animate-fade-in-up delay-${100 + index * 50}`}>
                    <Checkbox
                      id={`new-spec-${specialite.id}`}
                      checked={selectedSpecialiteIds.includes(specialite.id)}
                      onCheckedChange={(checked) => 
                        handleSpecialiteSelection(specialite.id, checked as boolean)
                      }
                      className="border-primary"
                    />
                    <label 
                      htmlFor={`new-spec-${specialite.id}`}
                      className="text-sm font-medium cursor-pointer smooth-transition hover:text-primary"
                    >
                      {specialite.nom}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Médicaments */}
            <div className="animate-fade-in-up delay-600">
              <Label htmlFor="medicaments" className="text-sm font-medium text-gray-700">
                Médicaments prescrits
              </Label>
              <Textarea
                id="medicaments"
                value={formData.medicaments}
                onChange={(e) => handleInputChange('medicaments', e.target.value)}
                className="mt-1 border-primary/30 focus:border-primary smooth-transition"
                rows={3}
                placeholder="Liste des médicaments et posologies..."
              />
            </div>

            {/* Notes */}
            <div className="animate-fade-in-up delay-700">
              <Label htmlFor="notes" className="text-sm font-medium text-gray-700">
                Notes médicales
              </Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                className="mt-1 border-primary/30 focus:border-primary smooth-transition"
                rows={4}
                placeholder="Observations, diagnostics, recommandations..."
              />
            </div>

            <Button
              type="submit"
              disabled={isSubmitting}
              className="w-full medical-gradient hover:opacity-90 text-white font-medium py-3 smooth-transition animate-fade-in-up delay-800"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Enregistrement...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Enregistrer le Patient
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Section de suppression des spécialités */}
      <Card className="border-red-200 shadow-lg card-hover animate-fade-in-up delay-900">
        <CardHeader className="bg-gradient-to-r from-red-500 to-red-600 text-white">
          <CardTitle className="flex items-center space-x-2">
            <Trash2 className="h-5 w-5" />
            <span>Gestion des Spécialités</span>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <Label className="text-sm font-medium text-gray-700">
              Supprimer des spécialités ({selectedForDeletion.length} sélectionnées)
            </Label>
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={selectAllForDeletion}
                disabled={selectedForDeletion.length === specialites.length}
                className="smooth-transition hover:bg-red-50"
              >
                Tout sélectionner
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={clearDeletionSelection}
                disabled={selectedForDeletion.length === 0}
                className="smooth-transition hover:bg-red-50"
              >
                Tout désélectionner
              </Button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 p-4 border rounded-lg bg-red-50 mb-4">
            {specialites.map((specialite, index) => (
              <div key={specialite.id} className={`flex items-center space-x-2 animate-fade-in-up delay-${100 + index * 50}`}>
                <Checkbox
                  id={`delete-spec-${specialite.id}`}
                  checked={selectedForDeletion.includes(specialite.id)}
                  onCheckedChange={(checked) => 
                    handleDeletionSelection(specialite.id, checked as boolean)
                  }
                  className="border-red-500"
                />
                <label 
                  htmlFor={`delete-spec-${specialite.id}`}
                  className="text-sm font-medium cursor-pointer smooth-transition hover:text-red-600"
                >
                  {specialite.nom}
                </label>
              </div>
            ))}
          </div>

          {selectedForDeletion.length > 0 && (
            <Button
              onClick={handleDeleteSpecialites}
              disabled={isDeleting}
              variant="destructive"
              className="w-full smooth-transition animate-scale-in"
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

export default PatientForm;