import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Users, Search, Edit, Trash2, Eye, Loader2, Download, FileText } from 'lucide-react';
import { usePatients } from '@/hooks/usePatients';
import EditPatientDialog from './EditPatientDialog';
import type { Patient } from '@/lib/supabase';

const PatientList = () => {
  const { patients, loading, deletePatient } = usePatients();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [editingPatient, setEditingPatient] = useState<Patient | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);

  const handleEditPatient = (patient: Patient) => {
    setEditingPatient(patient);
    setIsEditDialogOpen(true);
  };

  const handleDeletePatient = async (id: string) => {
    try {
      setDeletingId(id);
      await deletePatient(id);
    } catch (error) {
      // Error is handled in the hook
    } finally {
      setDeletingId(null);
    }
  };

  const generatePatientPDF = (patient: Patient) => {
    const content = `
FICHE PATIENT - DIAGNOSTIC MÉDICAL
=====================================

INFORMATIONS PERSONNELLES
-------------------------
Nom: ${patient.nom}
Prénom: ${patient.prenom}
Âge: ${patient.age} ans
Date de création: ${new Date(patient.created_at).toLocaleDateString('fr-FR')}
Dernière modification: ${new Date(patient.updated_at).toLocaleDateString('fr-FR')}

DONNÉES MÉDICALES
-----------------
Glycémie: ${patient.glycemie || 'Non renseignée'}
Tension Artérielle: ${patient.ta || 'Non renseignée'}
Taille: ${patient.taille > 0 ? `${patient.taille} cm` : 'Non renseignée'}
Poids: ${patient.poids > 0 ? `${patient.poids} kg` : 'Non renseigné'}
IMC: ${patient.imc > 0 ? patient.imc : 'Non calculé'}

SPÉCIALITÉS
-----------
Spécialité principale: ${patient.specialite || 'Non spécifiée'}
${patient.specialites && patient.specialites.length > 0 ? 
  `Spécialités supplémentaires:\n${patient.specialites.map(s => `- ${s.nom}`).join('\n')}` : 
  'Aucune spécialité supplémentaire'
}

MÉDICAMENTS PRESCRITS
--------------------
${patient.medicaments || 'Aucun médicament prescrit'}

NOTES MÉDICALES
---------------
${patient.notes || 'Aucune note médicale'}

=====================================
Document généré le ${new Date().toLocaleDateString('fr-FR')} à ${new Date().toLocaleTimeString('fr-FR')}
Système de Gestion Patients - Interface Médicale Professionnelle
    `;

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `diagnostic_${patient.nom}_${patient.prenom}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const generateAllPatientsPDF = async () => {
    try {
      setIsGeneratingPDF(true);
      
      let allContent = `
RAPPORT COMPLET - TOUS LES PATIENTS
===================================
Généré le ${new Date().toLocaleDateString('fr-FR')} à ${new Date().toLocaleTimeString('fr-FR')}
Nombre total de patients: ${patients.length}

`;

      patients.forEach((patient, index) => {
        allContent += `
${index + 1}. PATIENT: ${patient.prenom} ${patient.nom}
${'='.repeat(50)}

INFORMATIONS PERSONNELLES
-------------------------
Nom: ${patient.nom}
Prénom: ${patient.prenom}
Âge: ${patient.age} ans
Date de création: ${new Date(patient.created_at).toLocaleDateString('fr-FR')}

DONNÉES MÉDICALES
-----------------
Glycémie: ${patient.glycemie || 'Non renseignée'}
Tension Artérielle: ${patient.ta || 'Non renseignée'}
Taille: ${patient.taille > 0 ? `${patient.taille} cm` : 'Non renseignée'}
Poids: ${patient.poids > 0 ? `${patient.poids} kg` : 'Non renseigné'}
IMC: ${patient.imc > 0 ? patient.imc : 'Non calculé'}

SPÉCIALITÉS
-----------
Spécialité principale: ${patient.specialite || 'Non spécifiée'}
${patient.specialites && patient.specialites.length > 0 ? 
  `Spécialités supplémentaires:\n${patient.specialites.map(s => `- ${s.nom}`).join('\n')}` : 
  'Aucune spécialité supplémentaire'
}

MÉDICAMENTS: ${patient.medicaments || 'Aucun'}
NOTES: ${patient.notes || 'Aucune note'}

`;
      });

      allContent += `
=====================================
Fin du rapport - ${patients.length} patient(s) traité(s)
Système de Gestion Patients - Interface Médicale Professionnelle
`;

      const blob = new Blob([allContent], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `rapport_tous_patients_${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Erreur lors de la génération du PDF:', error);
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  const filteredPatients = patients.filter(patient =>
    patient.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.prenom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.specialite.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (patient.specialites && patient.specialites.some(s => 
      s.nom.toLowerCase().includes(searchTerm.toLowerCase())
    ))
  );

  const getIMCStatus = (imc: number) => {
    if (imc < 18.5) return { status: 'Insuffisant', color: 'bg-blue-100 text-blue-800' };
    if (imc < 25) return { status: 'Normal', color: 'bg-green-100 text-green-800' };
    if (imc < 30) return { status: 'Surpoids', color: 'bg-yellow-100 text-yellow-800' };
    return { status: 'Obésité', color: 'bg-red-100 text-red-800' };
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Chargement des patients...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="border-blue-200 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Users className="h-6 w-6" />
              <span>Liste des Patients ({patients.length})</span>
            </div>
            <Button
              onClick={generateAllPatientsPDF}
              disabled={isGeneratingPDF || patients.length === 0}
              variant="secondary"
              className="bg-white text-blue-600 hover:bg-gray-100"
            >
              {isGeneratingPDF ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Génération...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Télécharger Tous (PDF)
                </>
              )}
            </Button>
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
                            {patient.age} ans • {formatDate(patient.created_at)}
                          </p>
                        </div>
                        
                        <div>
                          <div className="space-y-1">
                            <Badge variant={patient.specialite ? 'default' : 'secondary'} className="mb-1">
                              {patient.specialite || 'Non spécifié'}
                            </Badge>
                            {patient.specialites && patient.specialites.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {patient.specialites.slice(0, 2).map((spec) => (
                                  <Badge key={spec.id} variant="outline" className="text-xs">
                                    {spec.nom}
                                  </Badge>
                                ))}
                                {patient.specialites.length > 2 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{patient.specialites.length - 2}
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>
                          {patient.ta && (
                            <p className="text-sm text-gray-600 mt-1">TA: {patient.ta}</p>
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
                                      <strong>Spécialité principale:</strong> {selectedPatient.specialite}
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

                                  {selectedPatient.specialites && selectedPatient.specialites.length > 0 && (
                                    <div>
                                      <strong>Toutes les spécialités:</strong>
                                      <div className="flex flex-wrap gap-2 mt-2">
                                        {selectedPatient.specialites.map((spec) => (
                                          <Badge key={spec.id} variant="outline">
                                            {spec.nom}
                                          </Badge>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                  
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
                                  
                                  <div className="text-xs text-gray-500 pt-2 border-t">
                                    Créé le: {formatDate(selectedPatient.created_at)}
                                    {selectedPatient.updated_at !== selectedPatient.created_at && (
                                      <span> • Modifié le: {formatDate(selectedPatient.updated_at)}</span>
                                    )}
                                  </div>

                                  <div className="flex gap-2 pt-4 border-t">
                                    <Button
                                      onClick={() => generatePatientPDF(selectedPatient)}
                                      className="flex-1 bg-green-500 hover:bg-green-600"
                                    >
                                      <FileText className="h-4 w-4 mr-2" />
                                      Télécharger Diagnostic (PDF)
                                    </Button>
                                  </div>
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
                            onClick={() => handleDeletePatient(patient.id)}
                            disabled={deletingId === patient.id}
                            className="text-red-600 hover:bg-red-50"
                          >
                            {deletingId === patient.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>

                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => generatePatientPDF(patient)}
                            className="text-green-600 hover:bg-green-50"
                          >
                            <Download className="h-4 w-4" />
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
      />
    </div>
  );
};

export default PatientList;