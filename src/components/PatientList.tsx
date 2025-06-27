import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { Users, Search, Edit, Trash2, Eye } from 'lucide-react';
import EditPatientDialog from './EditPatientDialog';

interface Patient {
  id: string;
  prenom: string;
  nom: string;
  age: number;
  glycemie: string;
  ta: string;
  taille: number;
  poids: number;
  imc: number;
  specialite: string;
  medicaments: string;
  notes: string;
  dateCreation: string;
}

const PatientList = () => {
  const { toast } = useToast();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [editingPatient, setEditingPatient] = useState<Patient | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = () => {
    const savedPatients = JSON.parse(localStorage.getItem('patients') || '[]');
    setPatients(savedPatients);
  };

  const deletePatient = (id: string) => {
    const updatedPatients = patients.filter(p => p.id !== id);
    setPatients(updatedPatients);
    localStorage.setItem('patients', JSON.stringify(updatedPatients));
    
    toast({
      title: "Patient supprimé",
      description: "Le patient a été supprimé avec succès.",
    });
  };

  const handleEditPatient = (patient: Patient) => {
    setEditingPatient(patient);
    setIsEditDialogOpen(true);
  };

  const handlePatientUpdated = () => {
    loadPatients();
  };

  const filteredPatients = patients.filter(patient =>
    patient.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.prenom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.specialite.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getIMCStatus = (imc: number) => {
    if (imc < 18.5) return { status: 'Insuffisant', color: 'bg-blue-100 text-blue-800' };
    if (imc < 25) return { status: 'Normal', color: 'bg-green-100 text-green-800' };
    if (imc < 30) return { status: 'Surpoids', color: 'bg-yellow-100 text-yellow-800' };
    return { status: 'Obésité', color: 'bg-red-100 text-red-800' };
  };

  return (
    <div className="space-y-6">
      <Card className="border-blue-200 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Users className="h-6 w-6" />
              <span>Liste des Patients ({patients.length})</span>
            </div>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="p-6">
          {/* Barre de recherche */}
          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Rechercher par nom, prénom ou spécialité..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 border-gray-300 focus:border-blue-500"
            />
          </div>

          {/* Liste des patients */}
          <div className="space-y-4">
            {filteredPatients.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                {patients.length === 0 ? 
                  "Aucun patient enregistré" : 
                  "Aucun patient trouvé pour cette recherche"
                }
              </div>
            ) : (
              filteredPatients.map((patient) => (
                <Card key={patient.id} className="border-l-4 border-l-blue-500 hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                          <h3 className="font-semibold text-lg text-gray-900">
                            {patient.prenom} {patient.nom}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {patient.age} ans • {patient.dateCreation}
                          </p>
                        </div>
                        
                        <div>
                          <Badge variant={patient.specialite ? 'default' : 'secondary'} className="mb-1">
                            {patient.specialite || 'Non spécifié'}
                          </Badge>
                          {patient.ta && (
                            <p className="text-sm text-gray-600">TA: {patient.ta}</p>
                          )}
                        </div>
                        
                        <div>
                          {patient.imc > 0 && (
                            <Badge className={getIMCStatus(patient.imc).color}>
                              IMC: {patient.imc} - {getIMCStatus(patient.imc).status}
                            </Badge>
                          )}
                          {patient.poids > 0 && patient.taille > 0 && (
                            <p className="text-sm text-gray-600 mt-1">
                              {patient.poids}kg • {patient.taille}cm
                            </p>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => setSelectedPatient(patient)}
                              >
                                <Eye className="h-4 w-4 mr-1" />
                                Voir
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                              <DialogHeader>
                                <DialogTitle>
                                  Fiche Patient - {selectedPatient?.prenom} {selectedPatient?.nom}
                                </DialogTitle>
                              </DialogHeader>
                              {selectedPatient && (
                                <div className="space-y-4">
                                  <div className="grid grid-cols-2 gap-4">
                                    <div>
                                      <strong>Âge:</strong> {selectedPatient.age} ans
                                    </div>
                                    <div>
                                      <strong>Spécialité:</strong> {selectedPatient.specialite}
                                    </div>
                                    <div>
                                      <strong>Poids:</strong> {selectedPatient.poids} kg
                                    </div>
                                    <div>
                                      <strong>Taille:</strong> {selectedPatient.taille} cm
                                    </div>
                                    <div>
                                      <strong>IMC:</strong> {selectedPatient.imc}
                                    </div>
                                    <div>
                                      <strong>TA:</strong> {selectedPatient.ta || 'Non renseignée'}
                                    </div>
                                  </div>
                                  
                                  {selectedPatient.glycemie && (
                                    <div>
                                      <strong>Glycémie:</strong> {selectedPatient.glycemie}
                                    </div>
                                  )}
                                  
                                  {selectedPatient.medicaments && (
                                    <div>
                                      <strong>Médicaments:</strong>
                                      <p className="mt-1 p-2 bg-gray-50 rounded text-sm">
                                        {selectedPatient.medicaments}
                                      </p>
                                    </div>
                                  )}
                                  
                                  {selectedPatient.notes && (
                                    <div>
                                      <strong>Notes médicales:</strong>
                                      <p className="mt-1 p-2 bg-gray-50 rounded text-sm">
                                        {selectedPatient.notes}
                                      </p>
                                    </div>
                                  )}
                                </div>
                              )}
                            </DialogContent>
                          </Dialog>
                          
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditPatient(patient)}
                            className="text-blue-600 hover:bg-blue-50"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => deletePatient(patient.id)}
                            className="text-red-600 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      <EditPatientDialog
        patient={editingPatient}
        isOpen={isEditDialogOpen}
        onClose={() => {
          setIsEditDialogOpen(false);
          setEditingPatient(null);
        }}
        onPatientUpdated={handlePatientUpdated}
      />
    </div>
  );
};

export default PatientList;
