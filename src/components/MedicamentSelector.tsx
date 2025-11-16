import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Search, Package, TriangleAlert as AlertTriangle, Plus, Minus } from 'lucide-react';
import { useMedicaments } from '@/hooks/useMedicaments';
import type { Medicament } from '@/types/database';

interface MedicamentSelectorProps {
  selectedMedicaments: { medicament: Medicament; quantite: number }[];
  onMedicamentToggle: (medicament: Medicament, selected: boolean, quantite?: number) => void;
  onQuantiteChange: (medicamentId: string, quantite: number) => void;
  customMedicaments: string;
  onCustomMedicamentsChange: (value: string) => void;
}

const MedicamentSelector = ({
  selectedMedicaments,
  onMedicamentToggle,
  onQuantiteChange,
  customMedicaments,
  onCustomMedicamentsChange
}: MedicamentSelectorProps) => {
  const { medicaments, familles, loading, updateStock } = useMedicaments();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredMedicaments = medicaments.filter(medicament =>
    medicament.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    medicament.famille?.nom.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const medicamentsParFamille = familles.map(famille => ({
    ...famille,
    medicaments: filteredMedicaments.filter(m => m.famille_id === famille.id)
  })).filter(famille => famille.medicaments.length > 0);

  const isMedicamentSelected = (medicamentId: string) => {
    return selectedMedicaments.some(sm => sm.medicament.id === medicamentId);
  };

  const getSelectedQuantite = (medicamentId: string) => {
    const selected = selectedMedicaments.find(sm => sm.medicament.id === medicamentId);
    return selected?.quantite || 1;
  };

  const handleMedicamentChange = (medicament: Medicament, checked: boolean) => {
    if (checked) {
      onMedicamentToggle(medicament, true, 1);
    } else {
      onMedicamentToggle(medicament, false);
    }
  };

  const handleQuantiteChange = (medicament: Medicament, delta: number) => {
    const currentQuantite = getSelectedQuantite(medicament.id);
    const newQuantite = Math.max(1, currentQuantite + delta);
    onQuantiteChange(medicament.id, newQuantite);
  };

  const getStockStatus = (medicament: Medicament) => {
    if (medicament.stock_actuel === 0) {
      return { status: 'Rupture', color: 'bg-red-100 text-red-800' };
    } else if (medicament.stock_actuel <= medicament.stock_minimum) {
      return { status: 'Stock faible', color: 'bg-orange-100 text-orange-800' };
    } else {
      return { status: 'Disponible', color: 'bg-green-100 text-green-800' };
    }
  };

  const handlePrescription = async () => {
    // Mettre à jour les stocks des médicaments prescrits
    for (const { medicament, quantite } of selectedMedicaments) {
      if (medicament.stock_actuel >= quantite) {
        await updateStock(medicament.id, medicament.stock_actuel - quantite);
      }
    }
  };

  if (loading) {
    return <div className="text-center py-4">Chargement des médicaments...</div>;
  }

  return (
    <div className="space-y-6">
      <Card className="border-blue-200 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardTitle className="flex items-center space-x-2">
            <Package className="h-5 w-5" />
            <span>Sélection des Médicaments</span>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="p-6 space-y-4">
          {/* Recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Rechercher un médicament..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Médicaments sélectionnés */}
          {selectedMedicaments.length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-800 mb-3">
                Médicaments prescrits ({selectedMedicaments.length})
              </h4>
              <div className="space-y-2">
                {selectedMedicaments.map(({ medicament, quantite }) => (
                  <div key={medicament.id} className="flex items-center justify-between bg-white p-2 rounded border">
                    <div className="flex-1">
                      <span className="font-medium">{medicament.nom}</span>
                      <span className="text-sm text-gray-600 ml-2">
                        {medicament.dosage} {medicament.forme}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleQuantiteChange(medicament, -1)}
                        disabled={quantite <= 1}
                      >
                        <Minus className="h-3 w-3" />
                      </Button>
                      <span className="w-8 text-center font-medium">{quantite}</span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleQuantiteChange(medicament, 1)}
                        disabled={quantite >= medicament.stock_actuel}
                      >
                        <Plus className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Liste des médicaments par famille */}
          <Accordion type="multiple" className="w-full">
            {medicamentsParFamille.map((famille) => (
              <AccordionItem key={famille.id} value={famille.id}>
                <AccordionTrigger className="text-left">
                  <div className="flex items-center justify-between w-full mr-4">
                    <span className="font-semibold">{famille.nom}</span>
                    <Badge variant="secondary">
                      {famille.medicaments.length} médicament(s)
                    </Badge>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-3 pt-2">
                    {famille.medicaments.map((medicament) => {
                      const stockStatus = getStockStatus(medicament);
                      const isSelected = isMedicamentSelected(medicament.id);
                      const selectedQuantite = getSelectedQuantite(medicament.id);
                      
                      return (
                        <div key={medicament.id} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                          <Checkbox
                            id={`med-${medicament.id}`}
                            checked={isSelected}
                            onCheckedChange={(checked) => 
                              handleMedicamentChange(medicament, checked as boolean)
                            }
                            disabled={medicament.stock_actuel === 0}
                          />
                          
                          <div className="flex-1">
                            <label 
                              htmlFor={`med-${medicament.id}`}
                              className="font-medium cursor-pointer"
                            >
                              {medicament.nom}
                            </label>
                            <div className="text-sm text-gray-600">
                              {medicament.dosage} {medicament.forme}
                              {medicament.description && (
                                <span className="block mt-1 text-xs">
                                  {medicament.description}
                                </span>
                              )}
                            </div>
                          </div>

                          <div className="text-right">
                            <Badge className={stockStatus.color}>
                              {stockStatus.status}
                            </Badge>
                            <div className="text-sm text-gray-600 mt-1">
                              Stock: {medicament.stock_actuel}
                            </div>
                            {medicament.prix_unitaire > 0 && (
                              <div className="text-sm font-medium text-green-600">
                                {medicament.prix_unitaire}€
                              </div>
                            )}
                          </div>

                          {isSelected && (
                            <div className="flex items-center space-x-1">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleQuantiteChange(medicament, -1)}
                                disabled={selectedQuantite <= 1}
                              >
                                <Minus className="h-3 w-3" />
                              </Button>
                              <span className="w-8 text-center text-sm font-medium">
                                {selectedQuantite}
                              </span>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleQuantiteChange(medicament, 1)}
                                disabled={selectedQuantite >= medicament.stock_actuel}
                              >
                                <Plus className="h-3 w-3" />
                              </Button>
                            </div>
                          )}

                          {medicament.stock_actuel <= medicament.stock_minimum && (
                            <AlertTriangle className="h-4 w-4 text-orange-500" />
                          )}
                        </div>
                      );
                    })}
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>

          {medicamentsParFamille.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Aucun médicament trouvé
            </div>
          )}
        </CardContent>
      </Card>

      {/* Médicaments personnalisés */}
      <Card className="border-gray-200 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Package className="h-5 w-5 text-gray-600" />
            <span>Médicaments Personnalisés</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div>
            <Label htmlFor="custom-medicaments" className="text-sm font-medium text-gray-700">
              Médicaments non disponibles en stock
            </Label>
            <Textarea
              id="custom-medicaments"
              value={customMedicaments}
              onChange={(e) => onCustomMedicamentsChange(e.target.value)}
              className="mt-1"
              rows={4}
              placeholder="Saisissez ici les médicaments prescrits qui ne sont pas disponibles dans le stock de la pharmacie..."
            />
            <p className="text-xs text-gray-500 mt-1">
              Ces médicaments seront ajoutés au champ "Médicaments prescrits" du patient
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MedicamentSelector;