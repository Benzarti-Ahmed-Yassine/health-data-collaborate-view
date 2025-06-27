import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { UserPlus, Save, Plus } from 'lucide-react';

interface Patient {
  id: string;
  prenom: string;
  nom: string;
  age: number;
  gynecologie: string;
  ta: string;
  taille: number;
  poids: number;
  imc: number;
  specialite: string;
  medicaments: string;
  notes: string;
  dateCreation: string;
}

const PatientForm = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    prenom: '',
    nom: '',
    age: '',
    gynecologie: '',
    ta: '',
    taille: '',
    poids: '',
    specialite: '',
    medicaments: '',
    notes: ''
  });
  const [customSpecialites, setCustomSpecialites] = useState<string[]>([]);
  const [newSpecialite, setNewSpecialite] = useState('');
  const [showAddSpecialite, setShowAddSpecialite] = useState(false);

  const defaultSpecialites = [
    'Généraliste', 'Pédodontiste', 'Orthophoniste',
    'Pédiatre', 'Cancérologue', 'Nutritionniste',
    'Gériatre', 'Gastro-entérologue', 'Ergothérapeute',
    'Endocrinologue', 'Pneumologue', 'Sage-femme',
    'Ophtalmologue', 'Gynécologue', 'Puéricultrice',
    'Cardiologue', 'Urologue',
    'Dentiste', 'Diabétologue'
  ];

  useEffect(() => {
    const savedSpecialites = JSON.parse(localStorage.getItem('customSpecialites') || '[]');
    setCustomSpecialites(savedSpecialites);
  }, []);

  const allSpecialites = [...defaultSpecialites, ...customSpecialites];

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculateIMC = () => {
    const poids = parseFloat(formData.poids);
    const taille = parseFloat(formData.taille) / 100; // conversion en mètres
    
    if (poids && taille) {
      return (poids / (taille * taille)).toFixed(2);
    }
    return '';
  };

  const addNewSpecialite = () => {
    if (newSpecialite.trim() && !allSpecialites.includes(newSpecialite.trim())) {
      const updatedCustomSpecialites = [...customSpecialites, newSpecialite.trim()];
      setCustomSpecialites(updatedCustomSpecialites);
      localStorage.setItem('customSpecialites', JSON.stringify(updatedCustomSpecialites));
      setFormData(prev => ({ ...prev, specialite: newSpecialite.trim() }));
      setNewSpecialite('');
      setShowAddSpecialite(false);
      
      toast({
        title: "Spécialité ajoutée",
        description: `La spécialité "${newSpecialite.trim()}" a été ajoutée avec succès.`,
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const imc = calculateIMC();
    const patient: Patient = {
      id: Date.now().toString(),
      prenom: formData.prenom,
      nom: formData.nom,
      age: parseInt(formData.age),
      gynecologie: formData.gynecologie,
      ta: formData.ta,
      taille: parseFloat(formData.taille),
      poids: parseFloat(formData.poids),
      imc: parseFloat(imc),
      specialite: formData.specialite,
      medicaments: formData.medicaments,
      notes: formData.notes,
      dateCreation: new Date().toLocaleDateString('fr-FR')
    };

    // Sauvegarde dans localStorage
    const patients = JSON.parse(localStorage.getItem('patients') || '[]');
    patients.push(patient);
    localStorage.setItem('patients', JSON.stringify(patients));

    toast({
      title: "Patient enregistré",
      description: `${patient.prenom} ${patient.nom} a été ajouté avec succès.`,
    });

    // Reset du formulaire
    setFormData({
      prenom: '', nom: '', age: '', gynecologie: '', ta: '', taille: '', poids: '',
      specialite: '', medicaments: '', notes: ''
    });
  };

  return (
    <div className="space-y-6">
      <Card className="border-blue-200 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardTitle className="flex items-center space-x-2">
            <UserPlus className="h-6 w-6" />
            <span>Fiche du Patient</span>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="p-6">
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
                <Label htmlFor="gynecologie" className="text-sm font-medium text-gray-700">
                  Gynécologie
                </Label>
                <Input
                  id="gynecologie"
                  value={formData.gynecologie}
                  onChange={(e) => handleInputChange('gynecologie', e.target.value)}
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

            {/* Spécialité avec option d'ajout */}
            <div>
              <Label htmlFor="specialite" className="text-sm font-medium text-gray-700">
                Spécialité *
              </Label>
              <div className="flex gap-2 mt-1">
                <Select value={formData.specialite} onValueChange={(value) => handleInputChange('specialite', value)}>
                  <SelectTrigger className="border-blue-200 focus:border-blue-500">
                    <SelectValue placeholder="Sélectionner une spécialité" />
                  </SelectTrigger>
                  <SelectContent>
                    {allSpecialites.map((spec) => (
                      <SelectItem key={spec} value={spec}>
                        {spec}
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
                    onClick={addNewSpecialite}
                    className="bg-green-500 hover:bg-green-600"
                  >
                    Ajouter
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

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium py-3"
            >
              <Save className="h-4 w-4 mr-2" />
              Enregistrer le Patient
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default PatientForm;
